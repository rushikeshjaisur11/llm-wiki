#!/usr/bin/env python3
"""
build_embeddings.py — semantic embedding index for Stage 2 vec re-rank.

Embeds title + tags + summary of every vault note using all-MiniLM-L6-v2 (384-d).
Stores 32-bit float vectors as BLOBs in wiki/embeddings.db for efficient cosine
re-ranking of FTS5 candidates in search.py Stage 2.

Dependencies: pip install sentence-transformers sqlite-vec

Usage:
  python build_embeddings.py              # full rebuild
  python build_embeddings.py --summary    # preview note count, no write
  python build_embeddings.py --update learning/foo/bar.md   # upsert one note
"""

import sys
import struct
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from build_graph import VAULT, parse_note, _should_include

try:
    import sqlite_vec          # type: ignore
    SQLITE_VEC_AVAILABLE = True
except ImportError:
    SQLITE_VEC_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer   # type: ignore
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

EMB_PATH   = VAULT / "wiki" / "embeddings.db"
MODEL_NAME = "all-MiniLM-L6-v2"


# ── DB helpers ────────────────────────────────────────────────────────────────

def _open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(EMB_PATH)
    if SQLITE_VEC_AVAILABLE:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
    return conn


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            path      TEXT PRIMARY KEY,
            embedding BLOB NOT NULL
        )
    """)
    conn.commit()


def _pack(vec) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


# ── Note collection ───────────────────────────────────────────────────────────

def _iter_notes():
    """Yield (node_id, embed_text) for every includable vault note."""
    for path in sorted(VAULT.rglob("*.md")):
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
        if not _should_include(rel):
            continue
        node = parse_note(path)
        tags_str = " ".join(node.get("tags", []))
        text = f"{node['title']} {tags_str} {node['summary']}".strip()
        if text:
            yield node["id"], text


# ── Build ─────────────────────────────────────────────────────────────────────

def full_build(model: "SentenceTransformer") -> None:
    pairs = list(_iter_notes())
    if not pairs:
        print("No notes found.")
        return

    ids  = [p[0] for p in pairs]
    docs = [p[1] for p in pairs]

    print(f"Encoding {len(docs)} notes with {MODEL_NAME}...")
    vecs = model.encode(
        docs,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    )

    conn = _open_db()
    _ensure_table(conn)
    conn.execute("DELETE FROM embeddings")
    conn.executemany(
        "INSERT OR REPLACE INTO embeddings (path, embedding) VALUES (?, ?)",
        [(nid, _pack(v)) for nid, v in zip(ids, vecs)],
    )
    conn.commit()
    conn.close()

    size = EMB_PATH.stat().st_size
    print(f"  wrote {EMB_PATH.relative_to(VAULT)}  ({size:,} bytes, {len(ids)} embeddings)")


def upsert_note(path_str: str, model: "SentenceTransformer") -> None:
    abs_path = VAULT / path_str
    if not abs_path.exists():
        print(f"ERROR: {path_str} not found", file=sys.stderr)
        sys.exit(1)

    node     = parse_note(abs_path)
    tags_str = " ".join(node.get("tags", []))
    text     = f"{node['title']} {tags_str} {node['summary']}".strip()

    vec = model.encode(text, normalize_embeddings=True)

    conn = _open_db()
    _ensure_table(conn)
    conn.execute(
        "INSERT OR REPLACE INTO embeddings (path, embedding) VALUES (?, ?)",
        (node["id"], _pack(vec)),
    )
    conn.commit()
    conn.close()
    print(f"  upserted {node['id']}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build semantic embedding index")
    parser.add_argument("--summary", action="store_true", help="Preview note count, no write")
    parser.add_argument("--update", metavar="PATH",
                        help="Upsert one note (vault-relative, e.g. learning/foo.md)")
    args = parser.parse_args()

    if not ST_AVAILABLE:
        print("sentence-transformers not installed.\n"
              "  pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        count = sum(1 for _ in _iter_notes())
        print(f"  Notes to embed: {count}")
        if EMB_PATH.exists():
            conn = sqlite3.connect(EMB_PATH)
            try:
                existing = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
                print(f"  Existing embeddings: {existing}")
            except sqlite3.OperationalError:
                print("  Existing embeddings: 0 (table not yet created)")
            conn.close()
        return

    print(f"Loading {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    if args.update:
        print(f"Upserting: {args.update}")
        upsert_note(args.update, model)
    else:
        full_build(model)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nDone [{now}]. Embeddings ready at wiki/embeddings.db")


if __name__ == "__main__":
    main()
