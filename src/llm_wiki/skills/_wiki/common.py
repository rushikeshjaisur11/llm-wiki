#!/usr/bin/env python3
"""
common.py — shared vault utilities for all wiki builders.

Provides:
  VAULT, TAG_COMMUNITIES, COMMUNITY_LABELS, INCLUDE_DIRS, EXCLUDE_PREFIXES
  GRAPH_DIR, GRAPH_JSON, EDGES_DIR, EDGES_JSON
  Helpers: _should_include, _node_id, _extract_summary
  Core:    parse_note, collect_notes, assign_community_tag
  Cache:   load_vault_notes() — parses all notes once, caches to disk (A1)
"""

import re
import sys
import yaml
import pickle
import hashlib
from pathlib import Path

# ── Vault resolution ─────────────────────────────────────────────────────────

def _resolve_vault() -> Path:
    config = Path(__file__).parent / ".vault_path"
    if config.exists():
        return Path(config.read_text(encoding="utf-8").strip())
    p = Path(__file__).parent
    for _ in range(5):
        p = p.parent
        if (p / "wiki" / "index.md").exists():
            return p
    raise FileNotFoundError(
        "Cannot find vault. Run /vault-setup or create skills/_wiki/.vault_path"
    )

VAULT      = _resolve_vault()
GRAPH_DIR  = VAULT / "wiki" / "graph"
GRAPH_JSON = VAULT / "wiki" / "graph.json"
EDGES_DIR  = GRAPH_DIR / "edges"
EDGES_JSON = GRAPH_DIR / "edges.json"   # legacy path kept for compatibility

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
    "attachments/",
}

# ── Tag → Community mapping (Tier 1) ────────────────────────────────────────

TAG_COMMUNITIES = {
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

# Single source of truth for community display labels (A6)
COMMUNITY_LABELS = {
    "rag":          "RAG & Vector Retrieval",
    "agents":       "Agents & Agentic Frameworks",
    "spark-delta":  "Spark, Streaming & Delta Lake",
    "python-core":  "Python Language & Tooling",
    "python":       "Python Language & Tooling",
    "fastapi":      "FastAPI & Web Services",
    "claude-code":  "Claude Code & AI Dev Tools",
    "llm-serving":  "LLM Serving & Inference",
    "data-infra":   "Data Infrastructure & GCP",
}

FOLDER_COMMUNITY_FALLBACK = {
    "data-engineering": "data-infra",
}

PATH_COMMUNITY_OVERRIDES = {
    "learning/fastapi/": "fastapi",
    "learning/building-generative-ai-services/": "fastapi",
    "learning/building-generative-ai-services-with-fastapi": "fastapi",
    "learning/python/": "python-core",
    "learning/git/": "python-core",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _should_include(rel_path: str) -> bool:
    top = rel_path.split("/")[0]
    if top not in INCLUDE_DIRS:
        return False
    for prefix in EXCLUDE_PREFIXES:
        if rel_path.startswith(prefix):
            return False
    return True


def _node_id(path: Path) -> str:
    return str(path.relative_to(VAULT).with_suffix("")).replace("\\", "/")


def _extract_summary(content: str, max_chars: int = 300) -> str:
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
        if len(line) >= 30:
            return line[:max_chars]

    return ""


def parse_note(path: Path) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    node_id = _node_id(path)

    fm: dict = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            try:
                fm = yaml.safe_load(content[3:end]) or {}
            except yaml.YAMLError:
                pass

    _IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
    raw_links = re.findall(r'(?<!\!)\[\[([^\]|#\n]+?)(?:\|[^\]]*)?\]\]', content)
    links_to = sorted({
        lnk.strip().replace("\\", "/").removesuffix(".md")
        for lnk in raw_links
        if "/" in lnk and not lnk.strip().lower().endswith(_IMAGE_EXTS)
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


def collect_notes() -> list[Path]:
    notes = []
    for path in sorted(VAULT.rglob("*.md")):
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
        if _should_include(rel):
            notes.append(path)
    return notes


def assign_community_tag(node: dict) -> str | None:
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

    top_folder = node["id"].split("/")[0]
    return FOLDER_COMMUNITY_FALLBACK.get(top_folder)


# ── Disk-cached vault loader (A1) ─────────────────────────────────────────────

_NOTES_CACHE = VAULT / "wiki" / ".notes_cache.pkl"


def _vault_fingerprint() -> str:
    """MD5 of all content-note paths + modification timestamps."""
    entries = []
    for path in sorted(VAULT.rglob("*.md")):
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
        if _should_include(rel):
            entries.append(f"{rel}:{path.stat().st_mtime_ns}")
    return hashlib.md5("\n".join(entries).encode()).hexdigest()


def load_vault_notes(force: bool = False) -> dict[str, dict]:
    """
    Return {node_id: parsed_note} for every content note in the vault.
    Results are cached to wiki/.notes_cache.pkl and reused as long as no
    note file changes (checked via path+mtime fingerprint).
    """
    fp = _vault_fingerprint()
    if not force and _NOTES_CACHE.exists():
        try:
            with _NOTES_CACHE.open("rb") as f:
                cached = pickle.load(f)
            if cached.get("fingerprint") == fp:
                return cached["notes"]
        except Exception:
            pass

    paths = collect_notes()
    notes: dict[str, dict] = {}
    for path in paths:
        try:
            node = parse_note(path)
            notes[node["id"]] = node
        except Exception as e:
            print(f"  WARNING: skipping {path.name} -- {e}", file=sys.stderr)

    try:
        with _NOTES_CACHE.open("wb") as f:
            pickle.dump({"fingerprint": fp, "notes": notes}, f, protocol=4)
    except Exception:
        pass

    return notes
