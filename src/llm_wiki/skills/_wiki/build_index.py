#!/usr/bin/env python3
"""
build_index.py — SQLite FTS5 search index + PMI synonym builder.

Produces:
  wiki/search.db      — FTS5 index (BM25 + Porter stemming, community pre-filter)
  wiki/synonyms.json  — auto-discovered term synonyms via co-occurrence PMI

FTS5 table schema:
  path (UNINDEXED), community (UNINDEXED), title [w:5], tags [w:8],
  section_headers [w:3], summary [w:2]

Usage:
  python build_index.py              # full rebuild
  python build_index.py --summary    # preview stats, no write
  python build_index.py --update learning/python/pydantic/07-custom-validators.md
"""

import re
import sys
import json
import math
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))
from common import (
    VAULT,
    parse_note,
    collect_notes,
    assign_community_tag,
    _should_include,
    _node_id,
    load_vault_notes,
)

DB_PATH  = VAULT / "wiki" / "search.db"
SYN_PATH = VAULT / "wiki" / "synonyms.json"

STOPWORDS = {
    "", "a", "an", "the", "in", "of", "to", "and", "or", "for",
    "vs", "with", "on", "at", "by", "is", "are", "how", "what",
    "when", "where", "why", "do", "does", "can", "i", "my", "me",
    "this", "that", "it", "as", "be", "was", "were", "via",
    "using", "use", "used", "e", "g", "ie",
}

# ── Section header extraction ─────────────────────────────────────────────────

def extract_section_headers(content: str) -> str:
    headers = []
    in_frontmatter = False
    fm_count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            fm_count += 1
            in_frontmatter = fm_count < 2
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("## ") or stripped.startswith("### "):
            text = re.sub(r"^#{2,3}\s+", "", stripped)
            text = re.sub(r"[*`_\[\]()]", "", text).strip()
            if text:
                headers.append(text)
    return " ".join(headers)


# ── Note enrichment ───────────────────────────────────────────────────────────

def enrich_note(path: Path) -> dict | None:
    """Parse note and add community + section_headers for indexing."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    node = parse_note(path)
    node["community"]       = assign_community_tag(node) or "uncategorized"
    node["section_headers"] = extract_section_headers(content)
    return node


def collect_enriched() -> list[dict]:
    """Load base notes from cache, then enrich with community + section headers."""
    notes_map = load_vault_notes()  # A1: disk-cached
    enriched  = []
    for nid, node in notes_map.items():
        n = dict(node)
        n["community"] = assign_community_tag(n) or "uncategorized"
        # section_headers requires re-reading the file — not stored in cache
        path = VAULT / (nid + ".md")
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                n["section_headers"] = extract_section_headers(content)
            except OSError:
                n["section_headers"] = ""
        else:
            n["section_headers"] = ""
        enriched.append(n)
    return enriched


# ── FTS5 index ────────────────────────────────────────────────────────────────

CREATE_SQL = """
CREATE VIRTUAL TABLE notes USING fts5(
    path             UNINDEXED,
    community        UNINDEXED,
    title,
    tags,
    section_headers,
    summary,
    tokenize = 'porter unicode61'
)
"""

def build_fts(notes: list[dict]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS notes")
    conn.execute(CREATE_SQL)
    rows = [
        (
            n["id"],
            n["community"],
            n["title"],
            " ".join(n["tags"]),
            n["section_headers"],
            n["summary"],
        )
        for n in notes
    ]
    conn.executemany("INSERT INTO notes VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def upsert_fts(path_str: str) -> None:
    """Incremental update: remove old row, insert new one. O(1)."""
    abs_path = VAULT / path_str
    if not abs_path.exists():
        print(f"ERROR: {path_str} not found", file=sys.stderr)
        sys.exit(1)

    n = enrich_note(abs_path)
    if not n:
        print(f"ERROR: could not parse {path_str}", file=sys.stderr)
        sys.exit(1)

    conn   = sqlite3.connect(DB_PATH)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "notes" not in tables:
        conn.execute(CREATE_SQL)

    conn.execute("DELETE FROM notes WHERE path = ?", (n["id"],))
    conn.execute(
        "INSERT INTO notes VALUES (?,?,?,?,?,?)",
        (n["id"], n["community"], n["title"],
         " ".join(n["tags"]), n["section_headers"], n["summary"]),
    )
    conn.commit()
    conn.close()
    print(f"  upserted {n['id']} -> {n['community']}")


# ── PMI co-occurrence synonyms (A4) ──────────────────────────────────────────

def _tokenise(text: str) -> list[str]:
    text   = re.sub(r"[`*_\[\](){}]", " ", text)
    tokens = re.split(r"[\s,/|.\-_]+", text.lower())
    return [
        t for t in tokens
        if t
        and t not in STOPWORDS
        and len(t) > 2
        and not t.isdigit()
        and not re.match(r"^\d+[a-z]?$", t)
    ]


def build_pmi_synonyms(
    notes: list[dict],
    min_pmi: float = 2.0,
    min_cooc: int = None,
    max_synonyms: int = 4,
) -> dict[str, list[str]]:
    """
    Compute PMI-based synonym map from corpus tags + summary tokens.

    A4 optimizations:
    - Two-pass: collect term_freq first, then filter singleton tokens before
      building the co-occurrence matrix — reduces O(V²) to O(V_valid²).
    - Counter.most_common() early-break in PMI scoring phase.
    """
    N = len(notes)
    if N < 10:
        return {}

    if min_cooc is None:
        min_cooc = max(4, N // 15)

    # Pass 1: term frequencies + tokenised doc sets
    term_freq: Counter  = Counter()
    doc_token_sets: list[frozenset] = []
    for note in notes:
        doc_tokens = frozenset(_tokenise(" ".join(note["tags"]) + " " + note["summary"]))
        doc_token_sets.append(doc_tokens)
        for t in doc_tokens:
            term_freq[t] += 1

    # A4: drop tokens appearing in only one document (guaranteed below min_cooc)
    valid_tokens = {t for t, c in term_freq.items() if c >= 2}

    # Pass 2: co-occurrence on filtered token sets
    cooc: dict[str, Counter] = defaultdict(Counter)
    for doc_tokens in doc_token_sets:
        filtered     = sorted(doc_tokens & valid_tokens)
        n_tok        = len(filtered)
        for i in range(n_tok):
            t1 = filtered[i]
            for j in range(i + 1, n_tok):
                cooc[t1][filtered[j]] += 1

    # Compute PMI; A4: use most_common() to break early once count < min_cooc
    synonyms: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for t1, counts in cooc.items():
        p_t1 = term_freq[t1] / N
        for t2, c in counts.most_common():
            if c < min_cooc:
                break  # sorted descending — safe to stop
            p_t2   = term_freq[t2] / N
            p_both = c / N
            if p_t1 == 0 or p_t2 == 0:
                continue
            pmi = math.log(p_both / (p_t1 * p_t2))
            if pmi >= min_pmi:
                synonyms[t1].append((t2, pmi))
                synonyms[t2].append((t1, pmi))

    result: dict[str, list[str]] = {}
    for term, pairs in synonyms.items():
        pairs.sort(key=lambda x: -x[1])
        result[term] = [p[0] for p in pairs[:max_synonyms]]

    return result


# ── Summary & reporting ───────────────────────────────────────────────────────

def print_summary(notes: list[dict], synonyms: dict) -> None:
    from collections import Counter as C
    comm_counts = C(n["community"] for n in notes)
    has_headers = sum(1 for n in notes if n["section_headers"])

    print(f"\n  Notes indexed:      {len(notes)}")
    print(f"  With sec. headers:  {has_headers} ({has_headers*100//len(notes)}%)")
    print(f"  PMI synonym pairs:  {sum(len(v) for v in synonyms.values()) // 2}")
    print(f"  DB path:            {DB_PATH.relative_to(VAULT)}")
    print()
    print(f"  {'Community':<18} {'Notes':>5}")
    print(f"  {'-'*18} {'-'*5}")
    for comm, cnt in sorted(comm_counts.items(), key=lambda x: -x[1]):
        print(f"  {comm:<18} {cnt:>5}")

    if synonyms:
        print("\n  Sample auto-synonyms (PMI):")
        shown = set()
        for term, syns in sorted(synonyms.items()):
            pair = tuple(sorted([term, syns[0]]))
            if pair not in shown:
                print(f"    {term} <-> {syns[0]}")
                shown.add(pair)
            if len(shown) >= 10:
                break
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build SQLite FTS5 search index")
    parser.add_argument("--summary", action="store_true", help="Preview only, no write")
    parser.add_argument("--update", metavar="PATH",
                        help="Upsert one note (vault-relative)")
    args = parser.parse_args()

    if args.update:
        print(f"Upserting: {args.update}")
        upsert_fts(args.update)
        return

    print("Loading vault notes (cached)...")
    notes = collect_enriched()

    print("Computing PMI synonyms...")
    synonyms = build_pmi_synonyms(notes)

    print_summary(notes, synonyms)

    if args.summary:
        return

    print("Building FTS5 index...")
    build_fts(notes)
    db_size = DB_PATH.stat().st_size
    print(f"  wrote {DB_PATH.relative_to(VAULT)}  ({db_size:,} bytes)")

    print("Writing synonyms...")
    SYN_PATH.write_text(json.dumps(synonyms, indent=2, sort_keys=True), encoding="utf-8")
    print(f"  wrote {SYN_PATH.relative_to(VAULT)}  ({SYN_PATH.stat().st_size:,} bytes, "
          f"{len(synonyms)} terms)")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nDone [{now}]. Index ready at wiki/search.db")


if __name__ == "__main__":
    main()
