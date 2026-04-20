#!/usr/bin/env python3
"""
build_graph.py — wiki knowledge graph builder.

Parses all vault content notes, extracts metadata + wikilinks,
runs two-tier community detection, writes:
  wiki/graph.json              — meta + community index (always compact)
  wiki/graph/nodes/<c>.json    — full node descriptors per community
  wiki/graph/edges/<c>.json    — adjacency lists sharded by community (A2)

Usage:
  python build_graph.py              # full rebuild
  python build_graph.py --summary    # preview communities, no write
  python build_graph.py --update learning/fastapi/01-Project1-Basic-Routing.md
                                     # upsert one note into existing graph
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from common import (
    VAULT, TAG_COMMUNITIES, COMMUNITY_LABELS, GRAPH_DIR, GRAPH_JSON,
    EDGES_DIR, EDGES_JSON,
    _should_include, _node_id,
    parse_note, collect_notes, assign_community_tag,
    PATH_COMMUNITY_OVERRIDES, FOLDER_COMMUNITY_FALLBACK,
    load_vault_notes,
)

# Re-export for backward compatibility with build_routing / build_index
__all__ = [
    "VAULT", "TAG_COMMUNITIES", "COMMUNITY_LABELS", "GRAPH_DIR", "GRAPH_JSON",
    "EDGES_DIR", "EDGES_JSON", "_should_include", "_node_id",
    "parse_note", "collect_notes", "assign_community_tag",
    "PATH_COMMUNITY_OVERRIDES", "FOLDER_COMMUNITY_FALLBACK", "load_vault_notes",
    "_extract_summary",
]
from common import _extract_summary  # noqa: F401  (re-exported)


# ── Community detection ───────────────────────────────────────────────────────

def refine_with_structure(nodes: dict, initial_assignments: dict) -> dict:
    """
    Tier 2: structural refinement using networkx greedy modularity.
    Re-assigns nodes whose link-neighbours are predominantly in a different
    community than their tag-based assignment.
    """
    try:
        import networkx as nx
        from networkx.algorithms.community import greedy_modularity_communities
    except ImportError:
        return initial_assignments

    G = nx.Graph()
    for nid, node in nodes.items():
        G.add_node(nid)
        for target in node["links_to"]:
            if target in nodes:
                G.add_edge(nid, target)

    if len(G.edges) == 0:
        return initial_assignments

    structural_comms = list(greedy_modularity_communities(G))

    struct_map: dict[str, int] = {}
    for i, comm_set in enumerate(structural_comms):
        for nid in comm_set:
            struct_map[nid] = i

    struct_to_tag_comm: dict[int, str] = {}
    for i, comm_set in enumerate(structural_comms):
        votes = Counter(
            initial_assignments.get(nid)
            for nid in comm_set
            if initial_assignments.get(nid)
        )
        if votes:
            struct_to_tag_comm[i] = votes.most_common(1)[0][0]

    assignments = dict(initial_assignments)
    for nid in nodes:
        if assignments.get(nid) is None:
            sci = struct_map.get(nid)
            if sci is not None and sci in struct_to_tag_comm:
                assignments[nid] = struct_to_tag_comm[sci]

    return assignments


def build_communities(nodes: dict, assignments: dict) -> dict:
    """Group nodes into community objects."""
    groups: dict[str, list[str]] = defaultdict(list)
    for nid, comm in assignments.items():
        if comm:
            groups[comm].append(nid)
    groups.setdefault("uncategorized", [
        nid for nid in nodes if not assignments.get(nid)
    ])

    communities = {}
    for comm_key, member_ids in groups.items():
        if not member_ids:
            continue

        all_tags: Counter = Counter()
        for nid in member_ids:
            for tag in nodes[nid]["tags"]:
                all_tags[tag.lower()] += 1

        top_tags = [t for t, _ in all_tags.most_common(8)]

        degree: Counter = Counter()
        for nid in member_ids:
            degree[nid] += len(nodes[nid]["links_to"])
            for other in member_ids:
                if nid in nodes[other]["links_to"]:
                    degree[nid] += 1
        non_archive = [nid for nid in degree if not nid.startswith("archive/")]
        hub_pool = Counter({nid: degree[nid] for nid in non_archive}) if non_archive else degree
        hub = hub_pool.most_common(1)[0][0] if hub_pool else member_ids[0]

        # Use unified COMMUNITY_LABELS from common (A6)
        label = COMMUNITY_LABELS.get(comm_key) or " ".join(top_tags[:3]).title()

        communities[comm_key] = {
            "label": label,
            "keywords": TAG_COMMUNITIES.get(comm_key, top_tags[:6]),
            "hub": hub,
            "size": len(member_ids),
            "node_ids": sorted(member_ids),
        }

    return communities


# ── Write outputs ─────────────────────────────────────────────────────────────

def write_graph(nodes: dict, communities: dict) -> None:
    """Write all graph files, with edges sharded by community (A2)."""
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    nodes_dir = GRAPH_DIR / "nodes"
    nodes_dir.mkdir(exist_ok=True)
    EDGES_DIR.mkdir(exist_ok=True)

    edge_count = sum(
        1 for node in nodes.values()
        for t in node["links_to"] if t in nodes
    )
    dangling = sum(
        1 for node in nodes.values()
        for t in node["links_to"] if t not in nodes
    )

    # 1. graph.json — meta + community index only
    graph_data = {
        "meta": {
            "version": "1",
            "built_at": datetime.now(timezone.utc).isoformat(),  # A5
            "vault": str(VAULT),
            "node_count": len(nodes),
            "edge_count": edge_count,
            "dangling_links": dangling,
            "community_count": len(communities),
        },
        "communities": communities,
    }
    GRAPH_JSON.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")

    # 2. graph/nodes/<community>.json — full node descriptors per community
    for comm_key, comm in communities.items():
        comm_nodes = {
            nid: {k: v for k, v in nodes[nid].items() if k != "id"}
            for nid in comm["node_ids"]
            if nid in nodes
        }
        out = {"community": comm_key, "nodes": comm_nodes}
        (nodes_dir / f"{comm_key}.json").write_text(
            json.dumps(out, indent=2), encoding="utf-8"
        )

    # 3. graph/edges/<community>.json — adjacency lists sharded by community (A2)
    for comm_key, comm in communities.items():
        shard = {
            nid: nodes[nid]["links_to"]
            for nid in comm["node_ids"]
            if nid in nodes and nodes[nid]["links_to"]
        }
        (EDGES_DIR / f"{comm_key}.json").write_text(
            json.dumps(shard, indent=2), encoding="utf-8"
        )


# ── Upsert (--update mode) ────────────────────────────────────────────────────

def upsert_note(rel_path: str) -> None:
    """
    Parse a single note and upsert it into the existing graph files.
    Reads/writes only the affected community shard for edges (A2).
    """
    path = VAULT / rel_path
    if not path.exists():
        print(f"ERROR: {path} does not exist")
        sys.exit(1)

    if not GRAPH_JSON.exists():
        print("graph.json not found -- running full build instead")
        full_build(write=True)
        return

    node = parse_note(path)
    nid = node["id"]

    graph_data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    communities = graph_data["communities"]

    comm = assign_community_tag(node) or "uncategorized"
    node_without_id = {k: v for k, v in node.items() if k != "id"}

    # Update community node file
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    (GRAPH_DIR / "nodes").mkdir(exist_ok=True)
    comm_file = GRAPH_DIR / "nodes" / f"{comm}.json"

    if comm_file.exists():
        comm_data = json.loads(comm_file.read_text(encoding="utf-8"))
    else:
        comm_data = {"community": comm, "nodes": {}}

    comm_data["nodes"][nid] = node_without_id
    comm_file.write_text(json.dumps(comm_data, indent=2), encoding="utf-8")

    # Update community index in graph.json
    if comm not in communities:
        communities[comm] = {
            "label": COMMUNITY_LABELS.get(comm, comm.replace("-", " ").title()),
            "keywords": TAG_COMMUNITIES.get(comm, node["tags"][:6]),
            "hub": nid,
            "size": 1,
            "node_ids": [nid],
        }
    else:
        if nid not in communities[comm]["node_ids"]:
            communities[comm]["node_ids"].append(nid)
            communities[comm]["size"] += 1

    graph_data["meta"]["node_count"] = sum(c["size"] for c in communities.values())
    graph_data["meta"]["built_at"] = datetime.now(timezone.utc).isoformat()  # A5
    GRAPH_JSON.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")

    # Update only the affected edges shard (A2)
    EDGES_DIR.mkdir(parents=True, exist_ok=True)
    shard_file = EDGES_DIR / f"{comm}.json"
    edges_data = json.loads(shard_file.read_text(encoding="utf-8")) if shard_file.exists() else {}
    if node["links_to"]:
        edges_data[nid] = node["links_to"]
    elif nid in edges_data:
        del edges_data[nid]
    shard_file.write_text(json.dumps(edges_data, indent=2), encoding="utf-8")

    print(f"Upserted: {nid} -> community '{comm}'")


# ── Full build ────────────────────────────────────────────────────────────────

def full_build(write: bool = True) -> tuple[dict, dict]:
    """Parse all notes via disk cache, detect communities, optionally write output."""
    print("Loading vault notes (cached)...")
    nodes = load_vault_notes()  # A1: uses disk cache
    print(f"  {len(nodes)} nodes")

    initial_assignments = {nid: assign_community_tag(n) for nid, n in nodes.items()}
    unassigned = sum(1 for v in initial_assignments.values() if v is None)
    print(f"  Tag-based: {len(nodes) - unassigned} assigned, {unassigned} unassigned")

    assignments = refine_with_structure(nodes, initial_assignments)
    still_unassigned = sum(1 for v in assignments.values() if v is None)
    print(f"  After structural refinement: {still_unassigned} still unassigned -> 'uncategorized'")

    communities = build_communities(nodes, assignments)

    if write:
        write_graph(nodes, communities)
        print(f"\nWrote:")
        print(f"  {GRAPH_JSON}")
        print(f"  {GRAPH_DIR}/nodes/ ({len(communities)} files)")
        print(f"  {EDGES_DIR}/ ({len(communities)} shards)")

    return nodes, communities


# ── Summary report ────────────────────────────────────────────────────────────

def print_summary(nodes: dict, communities: dict) -> None:
    graph_data = json.loads(GRAPH_JSON.read_text()) if GRAPH_JSON.exists() else {}
    meta = graph_data.get("meta", {})

    print("\n-- Graph Summary ------------------------------------------")
    print(f"  Nodes       : {len(nodes)}")
    print(f"  Edges       : {meta.get('edge_count', '?')}")
    print(f"  Dangling    : {meta.get('dangling_links', '?')} (wikilinks to missing notes)")
    print(f"  Communities : {len(communities)}")
    print()
    print(f"  {'Community':<20} {'Size':>5}  Hub")
    print(f"  {'-'*20} {'-'*5}  {'-'*40}")
    for key, c in sorted(communities.items(), key=lambda x: -x[1]["size"]):
        print(f"  {key:<20} {c['size']:>5}  {c['hub']}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build wiki knowledge graph")
    parser.add_argument("--summary", action="store_true",
                        help="Print community breakdown only, do not write files")
    parser.add_argument("--update", metavar="PATH",
                        help="Upsert a single note (relative to vault root)")
    args = parser.parse_args()

    if args.update:
        upsert_note(args.update)
        return

    nodes, communities = full_build(write=not args.summary)
    print_summary(nodes, communities)


if __name__ == "__main__":
    main()
