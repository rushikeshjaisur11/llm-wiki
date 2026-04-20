#!/usr/bin/env python3
"""
build_routing.py — 2-tier compact Markdown routing index.

Outputs:
  wiki/routing.md               — Tier 1: community keywords (~500 bytes, always constant)
  wiki/routing/<community>.md   — Tier 2: one compact line per node per community

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

sys.path.insert(0, str(Path(__file__).parent))
from common import (
    VAULT, TAG_COMMUNITIES, COMMUNITY_LABELS,
    parse_note, collect_notes, assign_community_tag,
    load_vault_notes,
    _node_id, _should_include,
    PATH_COMMUNITY_OVERRIDES, FOLDER_COMMUNITY_FALLBACK,
)

# ── Paths ─────────────────────────────────────────────────────────────────────

ROUTING_DIR   = VAULT / "wiki" / "routing"
ROUTING_INDEX = VAULT / "wiki" / "routing.md"

# ── Helpers ───────────────────────────────────────────────────────────────────

def node_to_line(node: dict) -> str:
    """Render one node as a compact pipe-delimited routing line."""
    path    = node["id"]
    tags    = ",".join(node["tags"][:12])
    summary = node["summary"].replace("|", "-")
    if len(summary) > 120:
        summary = summary[:117].rstrip() + "..."
    return f"{path} | {tags} | {summary}"


def build_all() -> dict[str, list[dict]]:
    """Load all notes via cache and group by community."""
    notes_map = load_vault_notes()  # A1: disk-cached
    communities: dict[str, list[dict]] = {c: [] for c in TAG_COMMUNITIES}
    communities["uncategorized"] = []

    for node in notes_map.values():
        comm = assign_community_tag(node) or "uncategorized"
        communities.setdefault(comm, []).append(node)

    for comm in communities:
        communities[comm].sort(key=lambda n: (-len(n["tags"]), n["id"]))

    return communities


# ── Writers ───────────────────────────────────────────────────────────────────

def write_tier1(communities: dict[str, list[dict]]) -> None:
    """Write wiki/routing.md — the tiny, O(1) community keyword index."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# wiki routing index | updated: {now}\n"]

    for comm, keywords in TAG_COMMUNITIES.items():
        label      = COMMUNITY_LABELS.get(comm, comm)
        kw_str     = ",".join(keywords)
        node_count = len(communities.get(comm, []))
        lines.append(f"{comm} | {kw_str}  <!-- {label} | {node_count} nodes -->")

    ROUTING_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {ROUTING_INDEX.relative_to(VAULT)}  ({ROUTING_INDEX.stat().st_size} bytes)")


def write_tier2(comm: str, nodes: list[dict]) -> None:
    """Write wiki/routing/<community>.md — compact node lines for one community."""
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    out  = ROUTING_DIR / f"{comm}.md"
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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
    Reads/writes only the affected community file, then refreshes only that
    community's node count in routing.md (A7).
    """
    abs_path = VAULT / rel_path
    if not abs_path.exists():
        print(f"ERROR: {rel_path} does not exist in vault", file=sys.stderr)
        sys.exit(1)

    node     = parse_note(abs_path)
    comm     = assign_community_tag(node) or "uncategorized"
    new_line = node_to_line(node)
    node_id  = node["id"]

    # Remove old entry from any community file that contains this node
    for existing_file in ROUTING_DIR.glob("*.md"):
        lines    = existing_file.read_text(encoding="utf-8").splitlines()
        filtered = [l for l in lines if not l.startswith(node_id + " |")]
        if len(filtered) != len(lines):
            existing_file.write_text("\n".join(filtered) + "\n", encoding="utf-8")
            print(f"  removed old entry from {existing_file.name}")

    # Append to (or create) the target community file
    target = ROUTING_DIR / f"{comm}.md"
    if target.exists():
        content = target.read_text(encoding="utf-8").rstrip()
        lines   = content.splitlines()
        if lines and lines[0].startswith("#"):
            # A3: count actual non-header, non-empty lines + 1 for the new node
            existing_node_count = sum(1 for l in lines[1:] if l.strip())
            new_count = existing_node_count + 1
            lines[0] = re.sub(r"nodes: \d+", f"nodes: {new_count}", lines[0])
        content = "\n".join(lines) + "\n" + new_line + "\n"
    else:
        now   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        label = COMMUNITY_LABELS.get(comm, comm)
        content = f"# {comm} | {label} | updated: {now} | nodes: 1\n{new_line}\n"

    target.write_text(content, encoding="utf-8")
    print(f"  upserted {node_id} -> {comm} ({target.name})")

    # A7: refresh only the affected community's count in routing.md
    if ROUTING_INDEX.exists():
        _refresh_tier1_count(comm)


def _refresh_tier1_count(affected_comm: str) -> None:
    """Update node count for a single community in routing.md (A7)."""
    comm_file = ROUTING_DIR / f"{affected_comm}.md"
    if not comm_file.exists():
        return
    count = sum(
        1 for l in comm_file.read_text(encoding="utf-8").splitlines()
        if l and not l.startswith("#")
    )
    lines     = ROUTING_INDEX.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        m = re.match(r"^(\w[\w-]*) \|", line)
        if m and m.group(1) == affected_comm:
            line = re.sub(r"\d+ nodes -->", f"{count} nodes -->", line)
        new_lines.append(line)
    ROUTING_INDEX.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def _refresh_all_tier1_counts() -> None:
    """Full refresh of all community counts in routing.md (used by full rebuild)."""
    lines     = ROUTING_INDEX.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        m = re.match(r"^(\w[\w-]*) \|", line)
        if m:
            comm      = m.group(1)
            comm_file = ROUTING_DIR / f"{comm}.md"
            if comm_file.exists():
                count = sum(
                    1 for l in comm_file.read_text(encoding="utf-8").splitlines()
                    if l and not l.startswith("#")
                )
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

    tier2_bytes = sum(
        sum(len(node_to_line(n)) + 1 for n in nodes)
        for nodes in communities.values()
    )
    tier1_bytes = sum(
        len(f"{c} | {','.join(kw)}\n") for c, kw in TAG_COMMUNITIES.items()
    ) + 50
    print(f"\n  Estimated routing.md size:      {tier1_bytes:>6} bytes")
    print(f"  Estimated routing/*.md total:   {tier2_bytes:>6} bytes")
    print(f"  Total routing overhead:         {tier1_bytes + tier2_bytes:>6} bytes\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build 2-tier compact routing index")
    parser.add_argument("--summary", action="store_true", help="Preview only, no write")
    parser.add_argument("--update", metavar="PATH",
                        help="Upsert one note (vault-relative path)")
    args = parser.parse_args()

    if args.update:
        print(f"Upserting: {args.update}")
        upsert_note(args.update)
        return

    print("Loading vault notes (cached)...")
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
