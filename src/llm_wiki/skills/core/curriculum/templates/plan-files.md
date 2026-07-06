# Plan File Templates — used by /curriculum A4

Write each section to its target path. Fill all `<placeholder>` values.
For the Mermaid block in plan.md: use `<br/>` inside node labels, never `\n`.

---

## Template: curricula/<slug>/plan.md

```markdown
---
title: "Curriculum: <goal>"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
status: active
curriculum_id: <UUID v4>
tags: [curriculum, <topic-tag>]
goal: "<goal>"
time_budget: "<X h/day · N days>"
starting_level: <level>
bias: <concept|practical|balanced>
target_outcome: "<one line from user>"
prerequisites: []
---

# Curriculum: <goal>

> [!tldr]
> Line 1: What you'll learn.
> Line 2: The path (Foundations → Core → Advanced → Capstone).
> Line 3: What the capstone delivers.

## Overview
- **Total time:** N days · ~M hours
- **Daily commitment:** X h/day
- **Phases:** Foundations (days 1–A) → Core (A–B) → Advanced (B–C) → Capstone (C–N)
- **Capstone:** <concrete deliverable description>

## Phase map

graph LR
  P1[Foundations<br/>Days 1–A] --> P2[Core<br/>Days A–B] --> P3[Advanced<br/>Days B–C] --> CAP[Capstone<br/>Days C–N]

## Concept coverage

> Every concept in this curriculum. Concepts with a [[link]] are covered by existing vault notes — no new note needed.

### Phase 1 — Foundations
- Topic group
  - Concept A [[existing-note]] ← vault already covers this
  - Concept B ← will be generated day 2

### Phase 2 — Core
...

### Phase 3 — Advanced
...

### Capstone
- Deliverable: <description>
- Tech used: <list>
- Evaluation criteria: <how you know it's good>

## Day-by-day schedule

> **`day_label` is the canonical title for each day** — a short (≤6 words) topic phrase. Reuse it verbatim in `progress.md` (Title column), every note's `day_label:` frontmatter, and the `.ics` SUMMARY. The concept note H1 is a separate declarative claim *derived from* the label (U1). Never reword the label between files.

| Day | Phase | Topic (day_label) | Key concepts | Practical | Est. | # notes |
|-----|-------|-------------------|-------------|-----------|------|---------|
| 1   | F     | ...               | ...         | ...       | Xh   | 1       |

## Datasets & tools

| Dataset | Source | Used in |
|---------|--------|---------|
| ...     | HuggingFace/`<name>` | day 5 |

| Tool | Version | Used in |
|------|---------|---------|
| ...  | ...     | days 3–7 |

## Reuses from vault

- [[note-id]] — covers day N concepts (no new file needed)

## Cross-curriculum prerequisites

<!-- populated if other curricula exist with overlapping topics -->

## Sources consulted

- <url> (accessed <YYYY-MM-DD>)
```

---

## Template: curricula/<slug>/progress.md

```markdown
---
title: "Progress: <goal>"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
curriculum: "[[curricula/<slug>/plan]]"
active_day: 0
---

# Progress: <goal>

## Checklist

| Day | Title | Concepts | Practical | Review | Grade | Notes |
|-----|-------|----------|-----------|--------|-------|-------|
| 1   | <day_label> | ☐   | ☐         | ☐      | —     |       |

## Reflections

<!-- Add notes here as you go: what's easy, what's hard, what to replan -->
```

---

## Template: curricula/index.md (upsert — create if missing, else append row)

```markdown
---
title: Curricula Index
active: <slug>
---

# Curricula

| Slug | Goal | Status | Days done | Started |
|------|------|--------|-----------|---------|
| [[curricula/<slug>/plan\|<slug>]] | <goal> | active | 0/<N> | <YYYY-MM-DD> |
```
