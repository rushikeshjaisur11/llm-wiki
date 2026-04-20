#!/usr/bin/env python3
"""
export_canvas.py — export wiki knowledge graph to Obsidian canvas format.

Layout:
  - Group nodes as community containers (bordered panels with labels)
  - Greedy 2-column packing (balanced heights)
  - Hub nodes highlighted in yellow
  - Edges: hub-to-hub cross-community only (keeps the canvas clean)
  - Adaptive community height based on node count

Usage:
  python export_canvas.py           # write wiki/graph.canvas
  python export_canvas.py --summary # print stats, no write
"""

import json
import math
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_graph import VAULT

GRAPH_JSON = VAULT / "wiki" / "graph.json"
NODES_DIR  = VAULT / "wiki" / "graph" / "nodes"
EDGES_DIR  = VAULT / "wiki" / "graph" / "edges"   # sharded per community
CANVAS_OUT = VAULT / "wiki" / "graph.canvas"

# Node sizing
NODE_W        = 280
NODE_H        = 58
NODE_GAP_X    = 24
NODE_GAP_Y    = 16
NODES_PER_ROW = 3

# Group container padding
GROUP_PAD_X   = 32   # left/right padding inside group
GROUP_PAD_TOP = 68   # space reserved for the group label header
GROUP_PAD_BOT = 32   # bottom padding

# Global spacing
GROUP_GAP_Y = 80    # vertical gap between communities in a column
COL_GAP_X   = 120   # horizontal gap between the two columns
NUM_COLS    = 2

# Hub highlight color (yellow = "3")
HUB_COLOR = "3"

# Community display labels and accent colors
# Obsidian accent colors: 1=red 2=orange 3=yellow 4=green 5=cyan 6=purple
COMM_META: dict[str, dict] = {
    "python-core":  {"label": "Python",              "color": "2"},
    "fastapi":      {"label": "FastAPI & AI Apps",   "color": "5"},
    "claude-code":  {"label": "Claude & Anthropic",  "color": "6"},
    "spark-delta":  {"label": "Spark & Delta Lake",  "color": "1"},
    "rag":          {"label": "RAG & Retrieval",     "color": "4"},
    "data-infra":   {"label": "Data Infrastructure","color": "1"},
    "agents":       {"label": "Agents & MCP",        "color": "6"},
    "llm-serving":  {"label": "LLM Serving",         "color": "2"},
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def uid() -> str:
    return str(uuid.uuid4())[:8]


def group_height(n_nodes: int) -> int:
    """Total pixel height of a community group for n_nodes."""
    rows = math.ceil(n_nodes / NODES_PER_ROW)
    content_h = rows * (NODE_H + NODE_GAP_Y) - NODE_GAP_Y
    return GROUP_PAD_TOP + content_h + GROUP_PAD_BOT


def group_width() -> int:
    """Fixed group width (same for all communities)."""
    return NODES_PER_ROW * (NODE_W + NODE_GAP_X) - NODE_GAP_X + 2 * GROUP_PAD_X


# ── Data loading ──────────────────────────────────────────────────────────────

def load_graph() -> dict:
    if not GRAPH_JSON.exists():
        print("wiki/graph.json not found — run build_graph.py first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))


def load_community_nodes(community: str) -> list[tuple[str, dict]]:
    path = NODES_DIR / f"{community}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes_dict = data.get("nodes", data) if isinstance(data, dict) else {}
    if isinstance(nodes_dict, dict):
        return list(nodes_dict.items())
    return []


def load_edges() -> dict[str, list[str]]:
    """Load edges from sharded per-community files in wiki/graph/edges/."""
    if not EDGES_DIR.exists():
        return {}
    merged: dict[str, list[str]] = {}
    for shard in EDGES_DIR.glob("*.json"):
        data = json.loads(shard.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for src, tgts in data.items():
                merged.setdefault(src, []).extend(tgts)
    return merged


# ── Layout ────────────────────────────────────────────────────────────────────

def greedy_2col_pack(items: list[tuple[str, int]]) -> tuple[list[str], list[str]]:
    """
    Greedy height-balanced packing into 2 columns.
    items: [(comm_key, n_nodes), ...] sorted by n_nodes desc.
    Returns (col0_keys, col1_keys) in top-to-bottom order.
    """
    cols: list[list[str]] = [[], []]
    heights: list[int] = [0, 0]
    for key, n in items:
        c = 0 if heights[0] <= heights[1] else 1
        cols[c].append(key)
        heights[c] += group_height(n) + GROUP_GAP_Y
    return cols[0], cols[1]


# ── Canvas building ───────────────────────────────────────────────────────────

def build_canvas(graph: dict) -> dict:
    communities = graph.get("communities", {})

    # Sort by size descending, then pack into 2 columns
    sorted_comms = sorted(
        [(k, v.get("size", 0)) for k, v in communities.items()],
        key=lambda x: -x[1],
    )
    col0, col1 = greedy_2col_pack(sorted_comms)
    columns = [col0, col1]
    size_map = dict(sorted_comms)

    gw = group_width()
    canvas_nodes: list[dict] = []
    canvas_edges: list[dict] = []
    id_map: dict[str, str] = {}  # node_path → canvas node id

    for col_idx, col_keys in enumerate(columns):
        col_x = col_idx * (gw + COL_GAP_X)
        cur_y = 0

        for comm_key in col_keys:
            comm_info = communities.get(comm_key, {})
            hub   = comm_info.get("hub", "")
            meta  = COMM_META.get(comm_key, {"label": comm_key.replace("-", " ").title(), "color": "4"})
            color = meta["color"]
            label = meta["label"]
            nodes = load_community_nodes(comm_key)
            if not nodes:
                continue

            n     = len(nodes)
            gh    = group_height(n)

            # Group container node (gives a bordered panel with label in Obsidian)
            canvas_nodes.append({
                "id":     uid(),
                "type":   "group",
                "x":      col_x,
                "y":      cur_y,
                "width":  gw,
                "height": gh,
                "label":  f"{label}  ·  {n} notes",
                "color":  color,
            })

            # File nodes placed inside the group bounds → auto-parented by Obsidian
            for ni, (nid, _) in enumerate(nodes):
                cid = uid()
                id_map[nid] = cid

                row = ni // NODES_PER_ROW
                col = ni % NODES_PER_ROW
                nx  = col_x + GROUP_PAD_X + col * (NODE_W + NODE_GAP_X)
                ny  = cur_y + GROUP_PAD_TOP + row * (NODE_H + NODE_GAP_Y)

                # Hub gets yellow highlight, others use community color
                node_color = HUB_COLOR if nid == hub else color

                canvas_nodes.append({
                    "id":     cid,
                    "type":   "file",
                    "file":   nid + ".md",
                    "x":      nx,
                    "y":      ny,
                    "width":  NODE_W,
                    "height": NODE_H,
                    "color":  node_color,
                })

            cur_y += gh + GROUP_GAP_Y

    # Edges — hub-to-hub cross-community only (avoids spaghetti)
    # Collect hub node ids
    hub_ids: set[str] = {
        communities[k].get("hub", "") for k in communities if communities[k].get("hub")
    }
    # Build node → community map
    node_comm: dict[str, str] = {}
    for comm_key in communities:
        for nid, _ in load_community_nodes(comm_key):
            node_comm[nid] = comm_key

    edges = load_edges()
    seen_pairs: set[tuple[str, str]] = set()
    for src_id, targets in edges.items():
        src_cid = id_map.get(src_id)
        if not src_cid:
            continue
        for tgt_id in targets:
            tgt_cid = id_map.get(tgt_id)
            if not tgt_cid:
                continue
            # Only draw edge if both endpoints are hubs AND in different communities
            if src_id not in hub_ids or tgt_id not in hub_ids:
                continue
            if node_comm.get(src_id) == node_comm.get(tgt_id):
                continue
            # Deduplicate bidirectional pairs
            pair = tuple(sorted([src_id, tgt_id]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            canvas_edges.append({
                "id":       uid(),
                "fromNode": src_cid,
                "toNode":   tgt_cid,
            })

    return {"nodes": canvas_nodes, "edges": canvas_edges}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    summary = "--summary" in sys.argv

    graph = load_graph()
    comms = graph.get("communities", {})
    total_nodes = sum(c.get("size", 0) for c in comms.values())
    edges_data  = load_edges()
    total_edges = sum(len(v) for v in edges_data.values())
    # Deduplicate bidirectional pairs for display count
    seen = set()
    for s, ts in edges_data.items():
        for t in ts:
            seen.add(tuple(sorted([s, t])))
    total_edges = len(seen)

    print(f"Communities: {len(comms)}  |  Nodes: {total_nodes}  |  Edges: {total_edges}")

    if summary:
        for key, c in sorted(comms.items(), key=lambda x: -x[1].get("size", 0)):
            print(f"  {key:<18} {c.get('size', 0):>4} notes  hub: {c.get('hub', '-')}")
        return

    canvas = build_canvas(graph)
    CANVAS_OUT.write_text(json.dumps(canvas, indent=2), encoding="utf-8")

    n_file_nodes = sum(1 for n in canvas["nodes"] if n["type"] == "file")
    n_groups     = sum(1 for n in canvas["nodes"] if n["type"] == "group")
    n_edges      = len(canvas["edges"])
    size         = CANVAS_OUT.stat().st_size

    print(f"  wrote {CANVAS_OUT.relative_to(VAULT)}")
    print(f"  {n_groups} community panels  |  {n_file_nodes} note cards  |  {n_edges} edges")
    print(f"  file size: {size:,} bytes")
    print(f"\nOpen wiki/graph.canvas in Obsidian to explore the knowledge graph.")


if __name__ == "__main__":
    main()
