#!/usr/bin/env python3
"""
build_routing.py — 2-tier compact Markdown routing index.

Outputs:
  wiki/routing.md               — Tier 1: community keywords (~500 bytes, always constant)
  wiki/routing/<community>.md   — Tier 2: one compact line per node per community

Token cost at scale:
  89 nodes  -> 0.5 KB + 4 KB   (vs current 9 KB + 9 KB JSON)
  300 nodes -> 0.5 KB + 13 KB  (vs current 30 KB + 30 KB JSON)
  1000 nodes-> 0.5 KB + 45 KB  (vs current 100 KB + 100 KB JSON)

Usage:
  python build_routing.py                                      # full rebuild
  python build_routing.py --summary                            # preview communities, no write
  python build_routing.py --update learning/python/pydantic/07-custom-validators.md
"""

import re
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ── Import shared logic from build_graph.py (same directory) ─────────────────

sys.path.insert(0, str(Path(__file__).parent))
from build_graph import (
    VAULT,
    TAG_COMMUNITIES,
    PATH_COMMUNITY_OVERRIDES,
    FOLDER_COMMUNITY_FALLBACK,
    parse_note,
    collect_notes,
    assign_community_tag,
    _node_id,
    _should_include,
)

# ── Paths ─────────────────────────────────────────────────────────────────────

ROUTING_DIR = VAULT / "wiki" / "routing"
ROUTING_INDEX = VAULT / "wiki" / "routing.md"

# ── Community display labels ──────────────────────────────────────────────────

COMMUNITY_LABELS = {
    "rag":         "RAG & Vector Retrieval",
    "agents":      "Agents & Agentic Frameworks",
    "spark-delta": "Spark, Streaming & Delta Lake",
    "python-core": "Python Language & Tooling",
    "fastapi":     "FastAPI & Web Services",
    "claude-code": "Claude Code & AI Dev Tools",
    "llm-serving": "LLM Serving & Inference",
    "data-infra":  "Data Infrastructure & GCP",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def node_to_line(node: dict) -> str:
    """Render one node as a compact pipe-delimited routing line."""
    path = node["id"]
    tags = ",".join(node["tags"][:12])          # cap at 12 tags to stay compact
    summary = node["summary"].replace("|", "-") # escape pipes in summary
    # Trim summary to 120 chars to keep lines scannable
    if len(summary) > 120:
        summary = summary[:117].rstrip() + "..."
    return f"{path} | {tags} | {summary}"


def build_all() -> dict[str, list[dict]]:
    """Parse all notes and group them by community. Returns {community: [nodes]}."""
    paths = collect_notes()
    communities: dict[str, list[dict]] = {c: [] for c in TAG_COMMUNITIES}
    communities["uncategorized"] = []

    for path in paths:
        node = parse_note(path)
        comm = assign_community_tag(node) or "uncategorized"
        communities.setdefault(comm, []).append(node)

    # Sort each community's nodes: hub (most tags) first, then alphabetical
    for comm in communities:
        communities[comm].sort(key=lambda n: (-len(n["tags"]), n["id"]))

    return communities


# ── Writers ───────────────────────────────────────────────────────────────────

def write_tier1(communities: dict[str, list[dict]]) -> None:
    """Write wiki/routing.md — the tiny, O(1) community keyword index."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# wiki routing index | updated: {now}\n"]

    for comm, keywords in TAG_COMMUNITIES.items():
        label = COMMUNITY_LABELS.get(comm, comm)
        kw_str = ",".join(keywords)
        node_count = len(communities.get(comm, []))
        lines.append(f"{comm} | {kw_str}  <!-- {label} | {node_count} nodes -->")

    ROUTING_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {ROUTING_INDEX.relative_to(VAULT)}  ({ROUTING_INDEX.stat().st_size} bytes)")


def write_tier2(comm: str, nodes: list[dict]) -> None:
    """Write wiki/routing/<community>.md — compact node lines for one community."""
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    out = ROUTING_DIR / f"{comm}.md"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    label = COMMUNITY_LABELS.get(comm, comm)
    header = f"# {comm} | {label} | updated: {now} | nodes: {len(nodes)}"

    node_lines = [node_to_line(n) for n in nodes]
    content = header + "\n" + "\n".join(node_lines) + "\n"

    out.write_text(content, encoding="utf-8")
    print(f"  wrote {out.relative_to(VAULT)}  ({out.stat().st_size} bytes, {len(nodes)} nodes)")


# ── Upsert (incremental update) ───────────────────────────────────────────────

def upsert_note(rel_path: str) -> None:
    """
    Update routing for a single note without a full rebuild.
    Removes any existing line for this note from all community files,
    then appends the updated line to the correct community file.
    O(1) update — reads/writes only the affected community file.
    """
    abs_path = VAULT / rel_path
    if not abs_path.exists():
        print(f"ERROR: {rel_path} does not exist in vault", file=sys.stderr)
        sys.exit(1)

    node = parse_note(abs_path)
    comm = assign_community_tag(node) or "uncategorized"
    new_line = node_to_line(node)
    node_id = node["id"]

    # Remove old entry from any community file that contains this node
    for existing_file in ROUTING_DIR.glob("*.md"):
        lines = existing_file.read_text(encoding="utf-8").splitlines()
        filtered = [l for l in lines if not l.startswith(node_id + " |")]
        if len(filtered) != len(lines):
            existing_file.write_text("\n".join(filtered) + "\n", encoding="utf-8")
            print(f"  removed old entry from {existing_file.name}")

    # Append to (or create) the target community file
    target = ROUTING_DIR / f"{comm}.md"
    if target.exists():
        content = target.read_text(encoding="utf-8").rstrip()
        # Update header node count
        lines = content.splitlines()
        if lines and lines[0].startswith("#"):
            lines[0] = re.sub(r"nodes: \d+", f"nodes: {content.count(chr(10))}", lines[0])
        content = "\n".join(lines) + "\n" + new_line + "\n"
    else:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        label = COMMUNITY_LABELS.get(comm, comm)
        content = f"# {comm} | {label} | updated: {now} | nodes: 1\n{new_line}\n"

    target.write_text(content, encoding="utf-8")
    print(f"  upserted {node_id} -> {comm} ({target.name})")

    # Also refresh tier1 node counts
    if ROUTING_INDEX.exists():
        _refresh_tier1_counts()


def _refresh_tier1_counts() -> None:
    """Update node counts in routing.md without rewriting content."""
    lines = ROUTING_INDEX.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        m = re.match(r"^(\w[\w-]*) \|", line)
        if m:
            comm = m.group(1)
            comm_file = ROUTING_DIR / f"{comm}.md"
            if comm_file.exists():
                count = sum(1 for l in comm_file.read_text(encoding="utf-8").splitlines()
                            if l and not l.startswith("#"))
                line = re.sub(r"\d+ nodes -->", f"{count} nodes -->", line)
        new_lines.append(line)
    ROUTING_INDEX.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


# ── Summary preview ───────────────────────────────────────────────────────────

def print_summary(communities: dict[str, list[dict]]) -> None:
    print("\n-- Community breakdown ------------------------------------------")
    print(f"  {'Community':<16} {'Nodes':>5}  {'Hub page'}")
    print(f"  {'-'*16} {'-'*5}  {'-'*40}")
    for comm, nodes in sorted(communities.items(), key=lambda x: -len(x[1])):
        hub = nodes[0]["id"] if nodes else "-"
        print(f"  {comm:<16} {len(nodes):>5}  {hub}")
    total = sum(len(v) for v in communities.values())
    print(f"\n  Total: {total} nodes across {len(communities)} communities")

    # Estimate output sizes
    tier2_bytes = sum(
        sum(len(node_to_line(n)) + 1 for n in nodes)
        for nodes in communities.values()
    )
    tier1_bytes = sum(
        len(f"{c} | {','.join(kw)}\n") for c, kw in TAG_COMMUNITIES.items()
    ) + 50  # header
    print(f"\n  Estimated routing.md size:      {tier1_bytes:>6} bytes")
    print(f"  Estimated routing/*.md total:   {tier2_bytes:>6} bytes")
    print(f"  Total routing overhead:         {tier1_bytes + tier2_bytes:>6} bytes")
    print(f"  (vs current JSON graph: ~{(9 + 9) * 1024:>5} bytes for a typical query)\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build 2-tier compact routing index")
    parser.add_argument("--summary", action="store_true", help="Preview only, no write")
    parser.add_argument("--update", metavar="PATH",
                        help="Upsert one note (vault-relative path, e.g. learning/foo.md)")
    args = parser.parse_args()

    if args.update:
        print(f"Upserting: {args.update}")
        upsert_note(args.update)
        return

    print("Scanning vault notes...")
    communities = build_all()
    print_summary(communities)

    if args.summary:
        return

    print("Writing routing files...")
    write_tier1(communities)
    for comm, nodes in communities.items():
        if nodes:
            write_tier2(comm, nodes)

    print("\nDone. Routing index rebuilt.")
    print(f"  Tier 1: {ROUTING_INDEX.relative_to(VAULT)}")
    print(f"  Tier 2: {ROUTING_DIR.relative_to(VAULT)}/<community>.md")


if __name__ == "__main__":
    main()
