---
name: audit
description: Quarterly full-vault health report. Runs stale scan, contradiction scan, orphan scan, stub scan, and dangling links. Produces a dated wiki/audit-YYYY-Q.md dashboard. Run once per quarter or on demand.
---

# Audit — Quarterly Full-Vault Health Report

Vault root: `{{VAULT}}/`

This skill is a superset of `/lint` focused on **knowledge quality and freshness** rather than file system issues. Run quarterly (or when confidence in vault freshness is low).

---

## Step 1: Determine quarter

Use today's date to label the report: `YYYY-Q<N>` (e.g. `2026-Q2`).
Check if `wiki/audit-YYYY-Q<N>.md` already exists. If so, ask: "An audit for this quarter already exists — overwrite or append?"

---

## Step 2: Staleness scan

Read TTL rules from `{{VAULT}}/SCHEMA.md`.
Scan frontmatter `last_verified` across all `.md` files in `learning/`, `research/`, `wiki/`.

Group by TTL class and days overdue:
```
## Staleness Report
| Topic class | Total notes | Overdue | Most overdue note | Days overdue |
|---|---|---|---|---|
| Framework APIs | 45 | 8 | langgraph/streaming | 127 |
| ...
```

Full list of overdue notes (sorted by most overdue):
```
| Note | last_verified | TTL | Days overdue | Suggested action |
```

---

## Step 3: Confidence scan

Count notes by confidence level across `learning/` and `research/`:
```
confidence: high    — N notes
confidence: medium  — N notes
confidence: low     — N notes
missing field       — N notes (need /ingest update or manual edit)
```

List all `confidence: low` notes.

---

## Step 4: Contradiction scan

For each community in `wiki/graph/nodes/`:
- Read the community `.json` file; compare `summary` and `tags` across members
- Flag pairs where summaries suggest opposing claims about the same concept
- Surface the `contradicts:` frontmatter field across the vault

Report:
```
## Contradictions
| Note A | Note B | Conflict description |
```
If no contradictions found, report: "No contradictions detected."

---

## Step 5: Orphan and dangling link scan

Orphans (no inbound links): list all `.md` files in `learning/`, `research/`, `data-engineering/` with zero inbound wikilinks.

Dangling links: wikilinks pointing to notes that don't exist (from `wiki/graph.json` if available, else grep-based).

---

## Step 6: Learning folder structure scan

For each runtime-tier folder (langgraph, langchain, google-adk, rag, fastapi, vector-db, llm-infra, agents):
- Check presence of: `index.md`, `production.md`, `cookbook.md`
- Report missing files

For all `learning/` folders:
- Check `index.md` exists; flag missing ones

---

## Step 7: Stubs

List any `.md` files with fewer than 20 lines of non-frontmatter content — these are stubs needing expansion.

---

## Step 8: Write audit report

Write `wiki/audit-YYYY-Q<N>.md`:

```markdown
---
title: Vault Audit — YYYY-Q<N>
created: <TODAY>
updated: <TODAY>
type: meta
---

# Vault Audit — YYYY-Q<N>

## Summary
- Total notes: N
- Overdue notes: N (X% of vault)
- Low/missing confidence: N notes
- Contradictions: N
- Orphans: N
- Dangling links: N
- Learning folders missing required files: N

## Priority Actions
1. Run `/refresh` on the N most overdue notes: [[note1]], [[note2]], ...
2. Add `production.md` to: langgraph, langchain, rag
3. Resolve contradictions: ...
4. Backfill `confidence` and `last_verified` on N notes missing these fields

## Staleness Detail
[table from Step 2]

## Confidence Distribution
[from Step 3]

## Contradictions
[from Step 4]

## Orphans & Dangling Links
[from Step 5]

## Learning Folder Gaps
[from Step 6]

## Stubs to Expand
[from Step 7]
```

---

## Step 9: Log

Append to `wiki/log.md`:
```
## [DATE] audit | Quarterly vault health — YYYY-Q<N>
- Report: [[wiki/audit-YYYY-Q<N>]]
- Overdue: N notes | Low confidence: N | Contradictions: N | Orphans: N
- Top action: <most important fix>
```
