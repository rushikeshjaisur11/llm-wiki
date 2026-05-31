---
name: graphbuild
description: Rebuild the wiki knowledge graph and search indexes from scratch. Runs build_graph.py, build_routing.py, build_index.py, and build_embeddings.py in sequence, prints a community breakdown table with node counts and hub notes, and reports dangling links. Use after bulk ingests or when community assignments need refreshing.
---

# Graphbuild — Rebuild the Wiki Knowledge Graph + Search Indexes

Vault root: `{{VAULT}}/`

## Step 1: Run all four builders in sequence

```
python {{SCRIPTS}}/build_graph.py
python {{SCRIPTS}}/build_routing.py
python {{SCRIPTS}}/build_index.py
python {{SCRIPTS}}/build_embeddings.py
```

- `build_graph.py` — builds `wiki/graph.json` (community assignments, edges, hub detection)
- `build_routing.py` — builds `wiki/routing.md` + `wiki/routing/<community>.md` (Stage 0 of search pipeline)
- `build_index.py` — builds `wiki/search.db` + `wiki/synonyms.json` (FTS5 BM25 search index + PMI synonyms)
- `build_embeddings.py` — builds `wiki/embeddings.db` (all-MiniLM-L6-v2 384-d embeddings for Stage 2 vec re-rank; requires `pip install sentence-transformers sqlite-vec`)

## Step 2: Read the output and print a community breakdown table

Read `{{VAULT}}/wiki/graph.json` and render the `communities` block as a table:

```
Community          | Nodes | Hub
-------------------|-------|------------------------------------------
rag                |    11 | research/rag-complete-guide
agents             |     5 | research/agentic-frameworks-cheatsheet
spark-delta        |     8 | data-engineering/databricks-data-engineering-course
...
```

## Step 3: Report totals + cluster health

From `graph.json.meta`, print:
- Total nodes
- Total edges
- Dangling links (wikilinks pointing to notes that don't exist)
- **Modularity score** (from `meta.modularity` if present, else compute as: `Q = (edges within communities) / (total edges) - expected`)

Per-community cluster health metrics:
```
Community   | Nodes | In-degree avg | Hub         | Leaves missing Up-link
------------|-------|---------------|-------------|------------------------
agents      |    12 |          3.4  | agents/index|  0
claude-code |    15 |          2.1  | claude-code/index| 0
...
```

A modularity score ≥ 0.5 indicates well-separated clusters (good for Obsidian graph view).
Score < 0.3 means the graph is too interconnected — wiki/index.md may still be linking to leaves directly.

Also report from `build_index.py` stdout:
- Notes indexed
- PMI synonym pairs discovered

## Step 4: Staleness subgraph report

After the community table, print two additional views:

**Stale subgraph** — notes where `today - last_verified > TTL_for_class(tags)`:
```
Stale notes (top 10 most overdue):
Note | last_verified | TTL class | Days overdue
```
Use TTL rules from `{{VAULT}}/SCHEMA.md`.

**Low-confidence subgraph** — notes where `confidence: low` or `confidence: medium` in frontmatter (top 10 by age):
```
Low-confidence notes:
Note | confidence | last_verified
```

These are informational — no action taken. The user can use `/refresh <note>` or `/audit` to address them.

## Step 5: Offer next actions

> Graph and search indexes rebuilt. Run `/graphbuild` again after more ingests, or use `python {{SCRIPTS}}/search.py "<query>"` to test search results. Run `/audit` for a full quarterly health report.
