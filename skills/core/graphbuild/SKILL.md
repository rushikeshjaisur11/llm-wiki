---
name: graphbuild
description: Rebuild the wiki knowledge graph from scratch. Runs build_graph.py, prints a community breakdown table with node counts and hub notes, and reports dangling links. Use after bulk ingests or when community assignments need refreshing.
---

# Graphbuild — Rebuild the Wiki Knowledge Graph

Vault root: `C:/Users/rushi/llm-wiki/`

## Step 1: Run the builder

```
python C:/Users/rushi/llm-wiki/wiki/build_graph.py
```

## Step 2: Read the output and print a community breakdown table

Read `C:/Users/rushi/llm-wiki/wiki/graph.json` and render the `communities` block as a table:

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

## Step 4: Offer next actions

> Graph rebuilt. Run with `--summary` to preview without writing, or `/graphbuild` again to refresh after more ingests.
