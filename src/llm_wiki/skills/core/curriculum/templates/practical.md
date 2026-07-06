<!-- PRACTICAL TEMPLATE — used by /curriculum B3
     Type: cookbook. Filename: practical.md inside day-<NN>/.
     Fill every section. All code must be version-pinned with latest stable confirmed via B1b.
     Quality Rubric: U1–U7 + C1–C6 (all checked in B5 before marking day done). -->

---
title: "Day <N>: Build <concrete artifact> using <technique>"
day_label: "<verbatim from plan.md Topic column>"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
last_verified: <YYYY-MM-DD>
confidence: high
provenance: generated+web
type: cookbook
maturity: seedling
needs_split: false
tags: [curriculum/<slug>, day-<NN>, practical, <topic-tags>]
curriculum: "[[curricula/<slug>/plan]]"
day: <N>
prerequisites: ["[[curricula/<slug>/day-<NN>/concepts]]"]
related: []
source: <dataset/library URL>
---

# Day <N>: <topic> — Practical

**Objective:** By the end of this practical you will have built `<concrete artifact>`.

## Setup

**Dataset:**

```python
# tested: <lib>==<version>
# How to get/generate the dataset.
# Prefer public: HuggingFace, Kaggle, sklearn built-ins, UCI.
# If none fits, generate fabricated data with a documented schema.
```

**Dependencies:**

```
pip install <packages>  # e.g. pandas==2.2.3 scikit-learn==1.5.2
```

## Step 1 — <name>

What you're doing and why.

```python
# tested: <lib>==<version>
<code>
```

**Expected output:**
```
<actual expected output — not a placeholder>
```

## Step 2 — ...

...

## Required outputs

> [!important] Your code must produce these exact files. The grader checks them — if they are missing or malformed, it fails.

| File | Description | Key requirements |
|------|-------------|-----------------|
| `curricula/<slug>/day-<NN>/outputs/day-<NN>-<artifact>.csv` | <what it contains> | rows: ~N, cols: [col1, col2, ...], no nulls in col1 |
| `curricula/<slug>/day-<NN>/outputs/day-<NN>-<artifact2>.json` | <what it contains> | keys: [key1, key2], values numeric |

> **Filename rule:** every output file name **must** start with `day-<NN>-` (e.g. `day-07-results.csv`). The save block, the checkpoint, and the grader (Flow F3) all parse the `## Required outputs` table verbatim — the table is the single source of truth. Never write a file with a different name than the one listed in this table.

Add one row per output file. Choose the simplest format that proves the work:
- tabular results → `.csv`
- metrics / config → `.json`
- trained model → `.pkl` (scikit-learn) or `.pt` (PyTorch)
- plot → `.png` (existence check only)

Ensure your Step code writes to these exact paths before moving on.

## Checkpoint

Run this to verify your outputs exist before submitting for grading:

```python
# tested: pathlib (stdlib)
import pathlib
outputs = [
    "curricula/<slug>/day-<NN>/outputs/day-<NN>-<artifact>.csv",
    # add one entry per Required output above — filenames must match the Required outputs table exactly
]
for p in outputs:
    assert pathlib.Path(p).exists(), f"Missing: {p}"
print("All outputs present — run `/curriculum grade <N>` to grade.")
```

## Stretch goals

1. <harder extension>
2. <harder extension>

## What can go wrong

| Error / symptom | Cause | Fix |
|----------------|-------|-----|
| ...             | ...   | ... |

## See also

- [[curricula/<slug>/day-<NN>/concepts]] — today's concepts
- [[curricula/<slug>/day-<NN>/review]] — today's review

## Recall prompts

> [!question] What is the exact command / function call to <key step in this practical>?

> [!answer]- <concrete answer with version-pinned syntax>

> [!question] What breaks if you skip <critical step>?

> [!answer]- <specific failure mode>
