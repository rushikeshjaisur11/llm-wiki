#!/usr/bin/env python3
"""
learningpath.py — generate a dependency-ordered reading list from the wiki knowledge graph.

Given a learning goal, finds the most relevant notes via search.py, then uses
wikilink graph structure to assign notes to tiers:
  foundations  — prerequisite notes (referenced by the main note or by many candidates)
  core         — the primary topic notes (top search results)
  advanced     — notes that build on the core topic (link TO the main note)

Usage:
  python learningpath.py "vLLM internals"
  python learningpath.py "Kafka architecture" --top 15

Output: JSON with foundations/core/advanced sections.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path

# ── Vault resolution (mirrors common.py) ─────────────────────────────────────

def _resolve_vault() -> Path:
    config = Path(__file__).parent / ".vault_path"
    if config.exists():
        return Path(config.read_text(encoding="utf-8").strip())
    p = Path(__file__).parent
    for _ in range(5):
        p = p.parent
        if (p / "wiki" / "index.md").exists():
            return p
    raise RuntimeError("Could not locate vault root (no wiki/index.md found).")

VAULT     = _resolve_vault()
WIKI      = VAULT / "wiki"
GRAPH_DIR = WIKI / "graph"
SEARCH_PY = Path(__file__).parent / "search.py"

# ── Graph loading ─────────────────────────────────────────────────────────────

def load_graph() -> tuple[dict, dict]:
    """
    Returns:
        nodes: {node_id: {title, tags, summary, links_to, ...}}
        edges: {node_id: [linked_node_id, ...]}
    Edge direction: A→B means note A contains [[B]] (B is referenced by A).
    """
    nodes: dict = {}
    edges: dict = {}

    nodes_dir = GRAPH_DIR / "nodes"
    edges_dir = GRAPH_DIR / "edges"

    if nodes_dir.exists():
        for f in nodes_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            nodes.update(data.get("nodes", {}))

    if edges_dir.exists():
        for f in edges_dir.glob("*.json"):
            if f.stem == "edges":   # skip legacy aggregate file
                continue
            data = json.loads(f.read_text(encoding="utf-8"))
            edges.update(data)

    return nodes, edges


def build_reverse_edges(edges: dict) -> dict:
    """reverse[B] = [A, ...] — nodes that link TO B."""
    reverse: dict = {}
    for src, targets in edges.items():
        for tgt in targets:
            reverse.setdefault(tgt, []).append(src)
    return reverse

# ── Search ────────────────────────────────────────────────────────────────────

def run_search(goal: str, top: int) -> list[str]:
    """Call search.py and return ordered list of node_ids (no .md suffix)."""
    result = subprocess.run(
        [sys.executable, str(SEARCH_PY), goal, "--top", str(top)],
        capture_output=True,
        text=True,
        cwd=str(VAULT),
    )
    lines = [
        line.strip().removesuffix(".md")
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() != "NO_RESULTS"
    ]
    return lines

# ── Reading time ──────────────────────────────────────────────────────────────

def estimate_reading_time(node_id: str) -> int:
    """Estimate reading time in minutes: max(10, round(words/200)*5)."""
    path = VAULT / (node_id + ".md")
    if not path.exists():
        return 15
    try:
        words = len(path.read_text(encoding="utf-8").split())
    except Exception:
        return 15
    return max(10, round(words / 200) * 5)

# ── Tier assignment ───────────────────────────────────────────────────────────

def assign_tiers(
    candidates: list[str],
    nodes: dict,
    edges: dict,
    reverse_edges: dict,
) -> tuple[list, list, list]:
    """
    Returns (foundations, core, advanced) as lists of node_ids.

    Logic:
      foundations — nodes that the main_node (top candidate) links TO
                    AND appear in candidates; plus candidates referenced
                    by >= 2 other candidates (high in-degree = foundational)
      core        — remaining top candidates (capped at 5), always includes main_node
      advanced    — candidates that link TO main_node and aren't in foundations
    """
    if not candidates:
        return [], [], []

    candidate_set = set(candidates)
    main_node = candidates[0]

    # Prerequisite signals
    main_links_to = set(edges.get(main_node, []))
    direct_prereqs = main_links_to & candidate_set

    # In-degree within candidate set: referenced by >= 2 candidates
    in_degree: dict = {}
    for c in candidates:
        for target in edges.get(c, []):
            if target in candidate_set and target != main_node:
                in_degree[target] = in_degree.get(target, 0) + 1
    crowd_sourced = {n for n, cnt in in_degree.items() if cnt >= 2}

    prereq_set = (direct_prereqs | crowd_sourced) - {main_node}

    # Extension signals: candidates that link TO main_node
    extension_set = {
        n for n in candidate_set
        if main_node in edges.get(n, []) and n not in prereq_set and n != main_node
    }

    # Build sections preserving search-rank order
    foundations = [c for c in candidates if c in prereq_set]
    core_raw    = [c for c in candidates if c not in prereq_set and c not in extension_set]
    advanced    = [c for c in candidates if c in extension_set]

    # Ensure main_node is first in core
    if main_node in foundations:
        foundations.remove(main_node)
    if main_node in advanced:
        advanced.remove(main_node)
    if main_node not in core_raw:
        core_raw.insert(0, main_node)
    else:
        core_raw.remove(main_node)
        core_raw.insert(0, main_node)

    # Cap core at 5; overflow goes to advanced
    core = core_raw[:5]
    advanced = core_raw[5:] + advanced

    return foundations, core, advanced

# ── Main ──────────────────────────────────────────────────────────────────────

def generate_path(goal: str, top: int = 12) -> dict:
    candidates = run_search(goal, top)
    if not candidates:
        return {"error": f"No relevant notes found for goal: {goal!r}"}

    nodes, edges = load_graph()
    reverse_edges = build_reverse_edges(edges)

    # Filter to real nodes only
    candidates = [c for c in candidates if c in nodes]
    if not candidates:
        return {"error": "Search returned results but none exist in the graph index. Run /graphbuild to rebuild."}

    foundations, core, advanced = assign_tiers(candidates, nodes, edges, reverse_edges)

    def fmt(node_ids: list) -> list[dict]:
        result = []
        for nid in node_ids:
            if nid not in nodes:
                continue
            n = nodes[nid]
            result.append({
                "id": nid,
                "title": n.get("title") or nid.split("/")[-1],
                "summary": (n.get("summary") or "")[:150].rstrip(),
                "tags": (n.get("tags") or [])[:6],
                "reading_time": estimate_reading_time(nid),
            })
        return result

    all_sections = foundations + core + advanced
    total_minutes = sum(estimate_reading_time(n) for n in all_sections if n in nodes)

    return {
        "goal": goal,
        "total_notes": len([n for n in all_sections if n in nodes]),
        "total_minutes": total_minutes,
        "foundations": fmt(foundations),
        "core": fmt(core),
        "advanced": fmt(advanced),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a learning path from the wiki knowledge graph.")
    parser.add_argument("goal", help="Learning goal or topic (e.g. 'vLLM internals')")
    parser.add_argument("--top", type=int, default=12, help="Number of search candidates (default: 12)")
    args = parser.parse_args()

    output = generate_path(args.goal, top=args.top)
    print(json.dumps(output, indent=2, ensure_ascii=False))
