# Quality Rubric — used by /curriculum B5

Score each generated file in turn. Print a PASS / FAIL line per criterion.
For any FAIL: regenerate the missing/failing section inline before proceeding to B6. Do not mark the day done with a failing check.
If all PASS: print `✓ Day <N> quality check passed` and continue to B6.

---

## concepts*.md — type `learning`

| # | Check | Pass? |
|---|-------|-------|
| U1 | Title is a declarative claim (not a noun phrase) | |
| U2 | `> [!tldr]` present, ≤3 lines, written in own words | |
| U3 | Note covers exactly one atomic concept (`needs_split: false`) | |
| U4 | 4–5 `> [!question]` / `> [!answer]-` pairs in `## Recall prompts` | |
| U5 | `source:` URL + `last_verified:` date in frontmatter | |
| U6 | `## See also` with ≥3 wikilinks | |
| U7 | `maturity: seedling` in frontmatter | |
| L1 | `## Intuition (mental model)` section present | |
| L2 | `## Formal definition` section present | |
| L3 | 2+ distinct `> [!example]` blocks with real code + real output | |
| L4 | `## Why does this work?` section present | |
| L5 | `## Diagram` (Mermaid) section present, uses `<br/>` not `\n` | |
| L6 | `## Common misconceptions` table present (≥1 row) | |
| L7 | `## Trade-offs vs alternatives` table present (≥2 alternatives) | |
| L8 | `## Sources` with ≥2 dated citations | |
| L9 | `day_label:` in frontmatter, verbatim match to plan.md Topic | |
| L10 | `confidence: high` and `level:` set in frontmatter | |
| L11 | `## Why this exists (motivation)` section present | |
| L12 | `## Cost & complexity` section present | |
| L13 | `## Edge cases & boundary conditions` section present | |
| L14 | `## Variations & extensions` section present | |

---

## practical.md — type `cookbook`

| # | Check | Pass? |
|---|-------|-------|
| U1–U7 | Universal rubric (same as above) | |
| C1 | All code blocks version-pinned (`# tested: lib==x.y`) with latest stable | |
| C2 | `## What can go wrong` table present (≥1 row) | |
| C3 | Prerequisite wikilink in frontmatter | |
| C4 | `## Required outputs` table present; filenames start `day-<NN>-` | |
| C5 | Checkpoint code block present; paths match Required outputs table | |
| C6 | `day_label:` in frontmatter, verbatim match to plan.md Topic | |

---

## review.md — type `reference`

| # | Check | Pass? |
|---|-------|-------|
| U1–U7 | Universal rubric | |
| R1 | `## Self-check questions` table (5–10 rows) | |
| R2 | `## See also` links to concepts, practical, next-day concepts | |
| R3 | `day_label:` in frontmatter and in H1 title | |
