---
name: graphbuild
description: Rebuild the wiki knowledge graph and search indexes from scratch. Runs build_graph.py, build_routing.py, and build_index.py in sequence, prints a community breakdown table with node counts and hub notes, and reports dangling links. Use after bulk ingests or when community assignments need refreshing.
---

# Graphbuild — Rebuild the Wiki Knowledge Graph + Search Indexes

Vault root: `{{VAULT}}/`

## Step 1: Run all three builders in sequence

```
python {{SCRIPTS}}/build_graph.py
python {{SCRIPTS}}/build_routing.py
python {{SCRIPTS}}/build_index.py
```

- `build_graph.py` — builds `wiki/graph.json` (community assignments, edges, hub detection)
- `build_routing.py` — builds `wiki/routing.md` + `wiki/routing/<community>.md` (Stage 0 of search pipeline)
- `build_index.py` — builds `wiki/search.db` + `wiki/synonyms.json` (FTS5 BM25 search index + PMI synonyms)

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

## Step 3: Report totals

From `graph.json.meta`, print:
- Total nodes
- Total edges
- Dangling links (wikilinks pointing to notes that don't exist)

Also report from `build_index.py` stdout:
- Notes indexed
- PMI synonym pairs discovered

## Step 4: Offer next actions

> Graph and search indexes rebuilt. Run `/graphbuild` again after more ingests, or use `python {{SCRIPTS}}/search.py "<query>"` to test search results.
