#!/usr/bin/env python3
"""
build_graph.py — wiki knowledge graph builder

Parses all vault content notes, extracts metadata + wikilinks,
runs two-tier community detection, writes:
  wiki/graph.json              — meta + community index (always compact)
  wiki/graph/nodes/<c>.json    — full node descriptors per community
  wiki/graph/edges.json        — full adjacency list

Usage:
  python build_graph.py              # full rebuild
  python build_graph.py --summary    # preview communities, no write
  python build_graph.py --update learning/fastapi/01-Project1-Basic-Routing.md
                                     # upsert one note into existing graph
"""

import re
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# ── Vault resolution ────────────────────────────────────────────────────────

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

VAULT = _resolve_vault()
GRAPH_DIR = VAULT / "wiki" / "graph"
GRAPH_JSON = VAULT / "wiki" / "graph.json"
EDGES_JSON = GRAPH_DIR / "edges.json"

# ── Include / Exclude ────────────────────────────────────────────────────────

INCLUDE_DIRS = ["research", "learning", "data-engineering", "archive"]

EXCLUDE_PREFIXES = {
    "data-engineering/sources/",
    ".claude/",
    "wiki/",
    "inbox/",
    "daily/",
    "personal/",
    "projects/",
}

# ── Tag → Community mapping (Tier 1) ────────────────────────────────────────

TAG_COMMUNITIES = {
    # Order matters: first community with strictly highest score wins.
    # Keep seed lists focused (<=10 tags) so scores stay comparable.
    "rag": [
        "rag", "retrieval-augmented-generation", "embeddings", "vector-db",
        "chunking", "reranking", "hybrid-search", "graphrag",
        "chromadb", "qdrant", "milvus", "multimodal-rag", "pgvector",
    ],
    "agents": [
        "langgraph", "agents", "agentic-ai", "multi-agent",
        "agentic-frameworks", "human-in-the-loop", "state-machine",
        "mcp", "tool-use", "orchestration",
        "llm-evaluation", "ragas", "deepeval", "langsmith",
        "evaluation", "hallucination", "faithfulness",
    ],
    "spark-delta": [
        "spark", "delta-lake", "dlt", "structured-streaming", "databricks",
        "kafka", "medallion", "pyspark", "delta-live-tables", "streaming",
        "unity-catalog", "governance", "liquid-clustering",
        "delta-sharing", "data-catalog",
    ],
    "fastapi": [
        "fastapi", "sqlalchemy", "jwt", "oauth2",
        "generative-ai", "rest-api", "routing", "pydantic-ai",
    ],
    "python-core": [
        "python", "pydantic", "asyncio", "type-hints", "decorators",
        "metaclasses", "generators", "concurrency", "python-intermediate",
        "dunder-methods", "context-managers", "git", "version-control",
    ],
    "claude-code": [
        "claude-code", "hooks", "skills", "anthropic",
        "claude-models", "prompting", "memory", "claude",
    ],
    "llm-serving": [
        "vllm", "bentoml", "gemini", "vertex-ai",
        "transformers", "model-serving", "inference", "flash-attention",
        "llm-serving", "batch-inference",
    ],
    "data-infra": [
        "bigquery", "airflow", "cloud-composer", "opentelemetry",
        "observability", "tracing", "gcp",
        "distributed-systems", "databases", "storage-engines",
        "systems-design", "replication", "partitioning",
    ],
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _should_include(rel_path: str) -> bool:
    """Return True if this relative path should be included as a content note."""
    top = rel_path.split("/")[0]
    if top not in INCLUDE_DIRS:
        return False
    for prefix in EXCLUDE_PREFIXES:
        if rel_path.startswith(prefix):
            return False
    return True


def _node_id(path: Path) -> str:
    """Convert absolute path to vault-relative node ID (no extension, forward slashes)."""
    return str(path.relative_to(VAULT).with_suffix("")).replace("\\", "/")


def _extract_summary(content: str, max_chars: int = 300) -> str:
    """
    Find first non-empty text line after ## Summary or ## TL;DR.
    Fallback: extract the first meaningful sentence/paragraph from the note body.
    """
    for header in ("## Summary", "## TL;DR"):
        idx = content.find(header)
        if idx < 0:
            continue
        after = content[idx + len(header):]
        for line in after.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("<!--") \
                    and not line.startswith(">") and not line.startswith("-"):
                return line[:max_chars]

    # Fallback: first prose paragraph after the frontmatter + H1 title
    body = content
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            body = content[end + 3:]

    SKIP_PREFIXES = ("#", "|", ">", "-", "*", "!", "[", "<!--")
    in_code_block = False
    for line in body.split("\n"):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        line = line.strip()
        if not line or any(line.startswith(p) for p in SKIP_PREFIXES):
            continue
        # Skip short fragments (< 30 chars) — likely stray words or YAML artifacts
        if len(line) >= 30:
            return line[:max_chars]

    return ""


def parse_note(path: Path) -> dict:
    """Extract structured metadata from a single vault note."""
    content = path.read_text(encoding="utf-8", errors="replace")
    node_id = _node_id(path)

    # Frontmatter
    fm: dict = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            try:
                fm = yaml.safe_load(content[3:end]) or {}
            except yaml.YAMLError:
                pass

    # Wikilinks → outbound edges
    raw_links = re.findall(r'\[\[([^\]|#\n]+?)(?:\|[^\]]*)?\]\]', content)
    links_to = sorted({
        lnk.strip().replace("\\", "/").removesuffix(".md")
        for lnk in raw_links
        if "/" in lnk
    })

    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    return {
        "id": node_id,
        "title": fm.get("title") or path.stem.replace("-", " ").title(),
        "tags": [str(t) for t in tags],
        "summary": _extract_summary(content),
        "type": str(fm.get("type") or ""),
        "date": str(fm.get("date") or ""),
        "links_to": links_to,
    }


# ── Community detection ──────────────────────────────────────────────────────

FOLDER_COMMUNITY_FALLBACK = {
    "data-engineering": "data-infra",
    # "research" and "archive" intentionally omitted — let structural refinement
    # assign them based on link neighbours rather than assuming rag.
}

# Path-prefix overrides — checked before tag scoring, take precedence.
# Use forward slashes; matched with startswith().
PATH_COMMUNITY_OVERRIDES = {
    "learning/fastapi/": "fastapi",
    "learning/building-generative-ai-services/": "fastapi",
    "learning/building-generative-ai-services-with-fastapi": "fastapi",
    "learning/python/": "python-core",
    "learning/git/": "python-core",
}

def assign_community_tag(node: dict) -> str | None:
    """Tier 1: tag-based community assignment with folder fallback."""
    # Path-prefix overrides take precedence over tag scoring
    for prefix, comm in PATH_COMMUNITY_OVERRIDES.items():
        if node["id"].startswith(prefix):
            return comm

    node_tags = {t.lower() for t in node["tags"]}
    best_comm, best_score = None, 0
    for comm, seed_tags in TAG_COMMUNITIES.items():
        score = len(node_tags & set(seed_tags))
        if score > best_score:
            best_score, best_comm = score, comm

    if best_comm:
        return best_comm

    # Folder-based fallback for untagged / sparse notes
    top_folder = node["id"].split("/")[0]
    return FOLDER_COMMUNITY_FALLBACK.get(top_folder)  # None if still unmatched


def refine_with_structure(nodes: dict, initial_assignments: dict) -> dict:
    """
    Tier 2: structural refinement using networkx greedy modularity.
    Re-assigns nodes whose link-neighbours are predominantly in a different community
    than their tag-based assignment.
    Returns updated assignments dict {node_id: community_key}.
    """
    try:
        import networkx as nx
        from networkx.algorithms.community import greedy_modularity_communities
    except ImportError:
        return initial_assignments  # skip if networkx unavailable

    G = nx.Graph()
    for nid, node in nodes.items():
        G.add_node(nid)
        for target in node["links_to"]:
            if target in nodes:
                G.add_edge(nid, target)

    if len(G.edges) == 0:
        return initial_assignments

    structural_comms = list(greedy_modularity_communities(G))

    # Build a map: node_id → structural community index
    struct_map: dict[str, int] = {}
    for i, comm_set in enumerate(structural_comms):
        for nid in comm_set:
            struct_map[nid] = i

    # For each structural community, find the dominant tag-community among its members
    struct_to_tag_comm: dict[int, str] = {}
    for i, comm_set in enumerate(structural_comms):
        votes = Counter(
            initial_assignments.get(nid)
            for nid in comm_set
            if initial_assignments.get(nid)
        )
        if votes:
            struct_to_tag_comm[i] = votes.most_common(1)[0][0]

    # Re-assign nodes that have no tag community but do have a structural community
    assignments = dict(initial_assignments)
    for nid in nodes:
        if assignments.get(nid) is None:
            sci = struct_map.get(nid)
            if sci is not None and sci in struct_to_tag_comm:
                assignments[nid] = struct_to_tag_comm[sci]

    return assignments


def build_communities(nodes: dict, assignments: dict) -> dict:
    """
    Group nodes into community objects.
    Returns dict {community_key: {label, keywords, hub, size, node_ids}}.
    """
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

        # Collect all tags from member nodes
        all_tags: Counter = Counter()
        for nid in member_ids:
            for tag in nodes[nid]["tags"]:
                all_tags[tag.lower()] += 1

        top_tags = [t for t, _ in all_tags.most_common(8)]

        # Hub = member with most outbound + inbound links
        degree: Counter = Counter()
        for nid in member_ids:
            degree[nid] += len(nodes[nid]["links_to"])
            for other in member_ids:
                if nid in nodes[other]["links_to"]:
                    degree[nid] += 1
        hub = degree.most_common(1)[0][0] if degree else member_ids[0]

        # Label from TAG_COMMUNITIES definition or top tags
        known_label = {
            "rag": "RAG & Vector Retrieval",
            "agents": "Agents & Agentic Frameworks",
            "spark-delta": "Spark, Streaming & Delta Lake",
            "python-core": "Python Language & Tooling",
            "python": "Python Language & Tooling",
            "fastapi": "FastAPI & Web Services",
            "claude-code": "Claude Code & AI Dev Tools",
            "llm-serving": "LLM Serving & Inference",
            "data-infra": "Data Infrastructure & GCP",
        }
        label = known_label.get(comm_key) or " ".join(top_tags[:3]).title()

        communities[comm_key] = {
            "label": label,
            "keywords": TAG_COMMUNITIES.get(comm_key, top_tags[:6]),
            "hub": hub,
            "size": len(member_ids),
            "node_ids": sorted(member_ids),
        }

    return communities


# ── Collect notes ────────────────────────────────────────────────────────────

def collect_notes() -> list[Path]:
    """Return all .md files that should be included as content notes."""
    notes = []
    for path in sorted(VAULT.rglob("*.md")):
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
        if _should_include(rel):
            notes.append(path)
    return notes


# ── Write outputs ─────────────────────────────────────────────────────────────

def write_graph(nodes: dict, communities: dict) -> None:
    """Write all three graph files."""
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    nodes_dir = GRAPH_DIR / "nodes"
    nodes_dir.mkdir(exist_ok=True)

    # Count valid edges
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
            "built_at": datetime.utcnow().isoformat(),
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

    # 3. graph/edges.json — full adjacency list
    edges = {
        nid: node["links_to"]
        for nid, node in nodes.items()
        if node["links_to"]
    }
    EDGES_JSON.write_text(json.dumps(edges, indent=2), encoding="utf-8")


# ── Upsert (--update mode) ────────────────────────────────────────────────────

def upsert_note(rel_path: str) -> None:
    """
    Parse a single note and upsert it into the existing graph files.
    Skips full community re-detection for speed.
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

    # Load existing graph
    graph_data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    communities = graph_data["communities"]

    # Assign community
    comm = assign_community_tag(node) or "uncategorized"
    node_without_id = {k: v for k, v in node.items() if k != "id"}

    # Update the community file
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
            "label": comm.replace("-", " ").title(),
            "keywords": TAG_COMMUNITIES.get(comm, node["tags"][:6]),
            "hub": nid,
            "size": 1,
            "node_ids": [nid],
        }
    else:
        if nid not in communities[comm]["node_ids"]:
            communities[comm]["node_ids"].append(nid)
            communities[comm]["size"] += 1

    graph_data["meta"]["node_count"] = sum(
        c["size"] for c in communities.values()
    )
    graph_data["meta"]["built_at"] = datetime.utcnow().isoformat()
    GRAPH_JSON.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")

    # Update edges
    edges_data = json.loads(EDGES_JSON.read_text(encoding="utf-8")) if EDGES_JSON.exists() else {}
    if node["links_to"]:
        edges_data[nid] = node["links_to"]
    EDGES_JSON.write_text(json.dumps(edges_data, indent=2), encoding="utf-8")

    print(f"Upserted: {nid} -> community '{comm}'")


# ── Full build ────────────────────────────────────────────────────────────────

def full_build(write: bool = True) -> tuple[dict, dict]:
    """Parse all notes, detect communities, optionally write output files."""
    note_paths = collect_notes()
    print(f"Parsing {len(note_paths)} notes...")

    nodes: dict[str, dict] = {}
    for path in note_paths:
        try:
            node = parse_note(path)
            nodes[node["id"]] = node
        except Exception as e:
            print(f"  WARNING: skipping {path.name} -- {e}")

    print(f"  {len(nodes)} nodes parsed")

    # Tier 1: tag-based assignment
    initial_assignments = {nid: assign_community_tag(n) for nid, n in nodes.items()}
    unassigned = sum(1 for v in initial_assignments.values() if v is None)
    print(f"  Tag-based assignment: {len(nodes) - unassigned} assigned, {unassigned} unassigned")

    # Tier 2: structural refinement (assigns remaining unassigned nodes)
    assignments = refine_with_structure(nodes, initial_assignments)
    still_unassigned = sum(1 for v in assignments.values() if v is None)
    print(f"  After structural refinement: {still_unassigned} still unassigned -> 'uncategorized'")

    communities = build_communities(nodes, assignments)

    if write:
        write_graph(nodes, communities)
        print(f"\nWrote:")
        print(f"  {GRAPH_JSON}")
        print(f"  {GRAPH_DIR}/nodes/ ({len(communities)} files)")
        print(f"  {EDGES_JSON}")

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
