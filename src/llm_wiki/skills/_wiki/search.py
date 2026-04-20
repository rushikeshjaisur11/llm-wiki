#!/usr/bin/env python3
"""
search.py — 3-stage wiki search. Zero token cost for Claude.

Stage 0  routing.md community match   (~500 bytes, O(1))
Stage 1  FTS5 BM25 with community pre-filter  (search.db, Porter stemming)
Stage 2  sqlite-vec semantic re-rank  (optional; requires sentence-transformers + sqlite-vec)

If wiki_search_daemon.py is running, search.py becomes a thin client:
queries are served from warm memory (~50ms) instead of cold load (~2-3s).

Usage:
  python search.py "LangGraph checkpointing"
  python search.py "kafka consumer groups" --top 3
  python search.py "pydantic field validators" --debug

Output: vault-relative .md paths, one per line.
        Prints NO_RESULTS when nothing matches.
"""

import re
import sys
import json
import socket
import sqlite3
import struct
import argparse
import difflib
from pathlib import Path

# ── Vault resolution ─────────────────────────────────────────────────────────

def _resolve_vault() -> Path:
    """Read vault path from .vault_path config (written by /vault-setup)."""
    config = Path(__file__).parent / ".vault_path"
    if config.exists():
        return Path(config.read_text(encoding="utf-8").strip())
    # Fallback: walk up from script looking for wiki/index.md
    p = Path(__file__).parent
    for _ in range(5):
        p = p.parent
        if (p / "wiki" / "index.md").exists():
            return p
    raise FileNotFoundError(
        "Cannot find vault. Run /vault-setup or create skills/_wiki/.vault_path"
    )

VAULT        = _resolve_vault()
DB_PATH      = VAULT / "wiki" / "search.db"
SYN_PATH     = VAULT / "wiki" / "synonyms.json"
ROUTING_PATH = VAULT / "wiki" / "routing.md"
EMB_PATH     = VAULT / "wiki" / "embeddings.db"
PORT_FILE    = VAULT / "wiki" / ".daemon_port"
HOST         = "127.0.0.1"

STOPWORDS = {
    "", "a", "an", "the", "in", "of", "to", "and", "or", "for",
    "vs", "with", "on", "at", "by", "is", "are", "how", "what",
    "when", "where", "why", "do", "does", "can", "i", "my", "me",
    "this", "that", "it", "as", "be", "was", "were", "via",
    "using", "use", "used",
}

# ── sqlite-vec detection (Stage 2 — optional) ─────────────────────────────────

try:
    import sqlite_vec  # type: ignore
    SQLITE_VEC_AVAILABLE = True
except ImportError:
    SQLITE_VEC_AVAILABLE = False


# ── Lazy model loader (avoids cold start when daemon is unavailable) ──────────

_model = None   # SentenceTransformer singleton


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ── Tokenisation ──────────────────────────────────────────────────────────────

def tokenise(text: str) -> list[str]:
    text = re.sub(r"[`*_\[\](){}]", " ", text)
    return [
        t for t in re.split(r"[\s,/|.\-_]+", text.lower())
        if t and t not in STOPWORDS and len(t) > 1
    ]


# ── Stage 0: Community match from routing.md ─────────────────────────────────

_communities: dict[str, set[str]] | None = None


def _load_communities() -> dict[str, set[str]]:
    global _communities
    if _communities is not None:
        return _communities
    if not ROUTING_PATH.exists():
        _communities = {}
        return _communities
    result = {}
    for line in ROUTING_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        comm = parts[0].strip()
        kw_raw = parts[1].split("<!--")[0].strip()
        keywords = {t for t in re.split(r"[\s,]+", kw_raw.lower()) if t}
        if comm and keywords:
            result[comm] = keywords
    _communities = result
    return result


def match_community(tokens: list[str]) -> str | None:
    comms = _load_communities()
    token_set = set(tokens)
    best_comm, best_score = None, 0
    for comm, keywords in comms.items():
        score = len(token_set & keywords)
        if score > best_score:
            best_score, best_comm = score, comm
    return best_comm if best_score > 0 else None


# ── Synonym expansion: PMI + fuzzy correction ─────────────────────────────────

_synonyms: dict[str, list[str]] | None = None


def _load_synonyms() -> dict[str, list[str]]:
    global _synonyms
    if _synonyms is not None:
        return _synonyms
    _synonyms = json.loads(SYN_PATH.read_text(encoding="utf-8")) if SYN_PATH.exists() else {}
    return _synonyms


def _known_terms() -> set[str]:
    return set(_load_synonyms().keys())


def fuzzy_correct(token: str, known: set[str]) -> str:
    if token in known:
        return token
    matches = difflib.get_close_matches(token, known, n=1, cutoff=0.85)
    return matches[0] if matches else token


def expand_query(tokens: list[str], debug: bool = False) -> set[str]:
    synonyms = _load_synonyms()
    known = _known_terms()
    expanded: set[str] = set()
    for t in tokens:
        corrected = fuzzy_correct(t, known)
        if corrected != t and debug:
            print(f"[debug] fuzzy: {t} -> {corrected}", file=sys.stderr)
        expanded.add(corrected)
        for syn in synonyms.get(corrected, []):
            expanded.add(syn)
            if debug:
                print(f"[debug] synonym: {corrected} -> {syn}", file=sys.stderr)
    return expanded


def build_fts_expr(expanded: set[str]) -> str:
    safe = [re.sub(r"[^\w]", "", t) for t in expanded if t]
    safe = [t for t in safe if len(t) > 1]
    if not safe:
        return ""
    return " OR ".join(safe)


# ── Stage 1: FTS5 BM25 search ─────────────────────────────────────────────────

# bm25() column weights: path=0, community=0, title=5, tags=8, section_headers=3, summary=2
BM25_WEIGHTS = "bm25(notes, 0, 0, 5, 8, 3, 2)"


def fts_search(fts_expr: str, community: str | None,
               limit: int, debug: bool) -> list[str]:
    if not DB_PATH.exists():
        if debug:
            print("[debug] search.db not found -- run build_index.py first", file=sys.stderr)
        return []

    conn = sqlite3.connect(DB_PATH)
    try:
        if community:
            sql = (f"SELECT path, {BM25_WEIGHTS} AS score "
                   f"FROM notes WHERE community=? AND notes MATCH ? "
                   f"ORDER BY score LIMIT ?")
            rows = conn.execute(sql, (community, fts_expr, limit)).fetchall()
            if debug:
                print(f"[debug] FTS5 community='{community}', expr='{fts_expr}', "
                      f"hits={len(rows)}", file=sys.stderr)
            if not rows:
                if debug:
                    print("[debug] community fallback -> full corpus", file=sys.stderr)
                sql = (f"SELECT path, {BM25_WEIGHTS} AS score "
                       f"FROM notes WHERE notes MATCH ? ORDER BY score LIMIT ?")
                rows = conn.execute(sql, (fts_expr, limit)).fetchall()
        else:
            sql = (f"SELECT path, {BM25_WEIGHTS} AS score "
                   f"FROM notes WHERE notes MATCH ? ORDER BY score LIMIT ?")
            rows = conn.execute(sql, (fts_expr, limit)).fetchall()
            if debug:
                print(f"[debug] FTS5 full corpus, expr='{fts_expr}', hits={len(rows)}", file=sys.stderr)

        if debug and rows:
            print(f"[debug] top scores: {[(r[0], round(r[1], 3)) for r in rows[:5]]}", file=sys.stderr)

        return [r[0] for r in rows]
    except sqlite3.OperationalError as e:
        if debug:
            print(f"[debug] FTS5 error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()


# ── Stage 2: sqlite-vec semantic re-rank ─────────────────────────────────────

def vec_rerank(query: str, candidates: list[str], top: int, debug: bool) -> list[str]:
    """
    Re-rank FTS5 candidates by cosine similarity using pre-built embeddings.
    candidates and return values use vault-relative paths WITHOUT .md suffix.
    Falls back to FTS5 order on any error or missing dependency.
    """
    if not SQLITE_VEC_AVAILABLE:
        return candidates

    if not EMB_PATH.exists():
        if debug:
            print("[debug] embeddings.db not found -- run build_embeddings.py", file=sys.stderr)
        return candidates

    try:
        model  = _get_model()
        q_vec  = model.encode(query, normalize_embeddings=True)
        q_blob = struct.pack(f"{len(q_vec)}f", *q_vec)

        placeholders = ",".join("?" * len(candidates))
        conn = sqlite3.connect(EMB_PATH)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)

        # Single batch query using native cosine distance — no N+1 loop
        rows = conn.execute(
            f"SELECT path, vec_distance_cosine(embedding, ?) AS dist "
            f"FROM embeddings WHERE path IN ({placeholders}) ORDER BY dist",
            (q_blob, *candidates),
        ).fetchall()
        conn.close()

        if debug:
            print(f"[debug] vec re-rank: {[(r[0], round(r[1], 3)) for r in rows[:5]]}", file=sys.stderr)

        ranked = [r[0] for r in rows]
        # Preserve FTS order for any candidates not in embeddings.db
        ranked_set = set(ranked)
        for c in candidates:
            if c not in ranked_set:
                ranked.append(c)

        return ranked[:top]

    except Exception as exc:
        if debug:
            print(f"[debug] vec re-rank skipped: {exc}", file=sys.stderr)
        return candidates


# ── Core search (no daemon) ───────────────────────────────────────────────────

def _local_search(query: str, top: int = 5, debug: bool = False) -> list[str]:
    """Run full 3-stage search locally (no daemon). Used by daemon itself."""
    tokens = tokenise(query)
    if not tokens:
        return []

    if debug:
        print(f"[debug] tokens: {tokens}", file=sys.stderr)

    community = match_community(tokens)
    if debug:
        print(f"[debug] community: {community}", file=sys.stderr)

    expanded = expand_query(tokens, debug=debug)
    fts_expr = build_fts_expr(expanded)
    if not fts_expr:
        return []

    candidates = fts_search(fts_expr, community, limit=top * 2, debug=debug)
    if not candidates:
        return []

    if SQLITE_VEC_AVAILABLE and EMB_PATH.exists() and len(candidates) > top:
        candidates = vec_rerank(query, candidates, top, debug=debug)

    return [p + ".md" for p in candidates[:top]]


# ── Daemon client ─────────────────────────────────────────────────────────────

def _try_daemon(query: str, top: int, debug: bool) -> list[str] | None:
    """Try the running daemon. Returns result list or None if daemon unavailable."""
    if not PORT_FILE.exists():
        return None
    try:
        port = int(PORT_FILE.read_text().strip())
        s = socket.create_connection((HOST, port), timeout=2)
        s.sendall((json.dumps({"query": query, "top": top, "debug": debug}) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
        s.close()
        resp = json.loads(buf.split(b"\n")[0].decode())
        if resp.get("error"):
            return None
        if debug:
            print("[debug] served by daemon", file=sys.stderr)
        return resp["results"]
    except Exception:
        return None


# ── Public search entry point ─────────────────────────────────────────────────

def search(query: str, top: int = 5, debug: bool = False) -> list[str]:
    """Try daemon first (warm model), fall back to local 3-stage search."""
    result = _try_daemon(query, top, debug)
    if result is not None:
        return result
    return _local_search(query, top=top, debug=debug)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="3-stage wiki search: community route -> FTS5 BM25 -> optional vec re-rank"
    )
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--top",   type=int, default=5,  help="Max results (default: 5)")
    parser.add_argument("--debug", action="store_true",  help="Show stage details on stderr")
    args = parser.parse_args()

    query   = " ".join(args.query)
    results = search(query, top=args.top, debug=args.debug)

    if not results:
        print("NO_RESULTS")
        sys.exit(0)

    for path in results:
        print(path)


if __name__ == "__main__":
    main()
