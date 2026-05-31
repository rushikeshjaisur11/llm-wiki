---
name: lint
description: Full vault health-check — scans for file system issues (misplaced files, junk, duplicates, unprocessed inbox) and wiki knowledge issues (orphan pages, broken wikilinks, concept stubs, contradictions). Add --quarterly for the full audit report (replaces /audit). Reports first, executes after confirmation.
---

# Lint — Full Vault Health Check

Vault root: `{{VAULT}}/`

## Argument parsing

| Invocation | Behaviour |
|---|---|
| `/lint` | Standard health check — file system + wiki quality (flat v2 rubric) |
| `/lint --typed` | Standard + typed-rubric report: U1/U3/U4/U7 per-folder coverage, maturity distribution, U4 gap table, hub inventory. Writes both `wiki/lint-YYYY-MM-DD.md` (flat) and `wiki/lint-typed-YYYY-MM-DD.md` (typed). |
| `/lint --quarterly` | Everything in standard + confidence scan + writes `wiki/audit-YYYY-Q<N>.md`. Run once per quarter. |

---

## Phase 1: Scan (read-only)

### File System Health

**1a. Loose root files**
List all files at vault root other than: `CLAUDE.md`, `SCHEMA.md`, `wiki/`, `learning/`, `research/`, `data-engineering/`, `projects/`, `personal/`, `archive/`, `attachments/`, `inbox/`, `daily/`.
Flag any `.md` files at the root level — the only sanctioned root `.md` file is `CLAUDE.md`.
Note: `wiki/memory.md` is a sanctioned file (written by `/tldr`) — do NOT flag it.

**1b. Unprocessed inbox/**
`Glob inbox/*` — list all files. PDFs/docs → `/ingest`. Already-markdown files → classify and move.

**1c. Duplicate files**
Files with same name but different casing or very similar names in the same folder.

**1d. Misplaced files**
Check each file's content against folder rules:
- `daily/` — must be dated `YYYY-MM-DD.md`; anything else is misplaced
- `learning/` — study notes organized by technology subfolder; loose `.md` files directly in `learning/` (not in a subfolder) are misplaced
  - `learning/python/` — Python language notes
  - `learning/python/tooling/` — uv, ruff, pyproject.toml, etc.
  - `learning/fastapi/` — FastAPI course (numbered 01-06) + `genai-services/` subfolder
  - `learning/git/` — Git notes
  - `learning/google-adk/` — Google ADK notes (concept files + production, evaluation, etc.)
- `research/` — deep technical dives, papers, LLMs, agents
- `data-engineering/` — GCP, Kafka, Airflow, BigQuery, pipelines
- `projects/` — specific active project notes
- `resources/` — bookmarks, links, tool references
- `personal/` — non-work notes
- `archive/` — completed/old work

**1e. Empty or near-empty folders**
Folders with 0 or 1 file — flag for review.

**1f. Junk file types**
`.pdf` anywhere outside `inbox/` or `sources/`, `.tmp`, `.bak`, `.DS_Store`, `desktop.ini`, `Thumbs.db`
Image files (`.png .jpg .jpeg .gif .svg .webp`) are **not junk** when located under `attachments/`. Flag image files found outside `attachments/` (except `inbox/`) as misplaced — suggest moving them to `attachments/`.

**1g. Scattered master summaries**
Find all `MASTER_SUMMARY.md` and `master-summary*.md` files across `outputs/` and `archive/outputs/`.
Plan: consolidate into a single `archive/outputs/master-summary.md` (one `## YYYY-MM-DD (Batch N)` section per original, with wikilinks to filed notes), then delete originals.

---

### Wiki Knowledge Health

**2a. Not in index**
Compare all `.md` files in `research/`, `learning/`, `data-engineering/` against `wiki/index.md`.
List pages present on disk but missing from the index.

**2b. Broken wikilinks**
`Grep` for `\[\[.*\]\]` patterns across all vault `.md` files.
For each link:
- If the target ends in an image extension (`.png .jpg .jpeg .gif .svg .webp`): check that `attachments/<filename>` exists on disk — do NOT look for a `.md` file. A missing image file is a broken embed, not a broken wikilink.
- Otherwise: check the target `.md` file exists. List broken ones with the file that contains them.
Do not flag `![[attachments/...]]` image embeds as broken if the file is present in `attachments/`.

**2b-triage. Dangling-link triage** (runs immediately after 2b detects broken wikilinks)

For each broken wikilink `[[X]]` found in 2b, classify it into one of three buckets:

**Bucket 1 — Rename (auto-fix):**
Fuzzy-match `X` against all existing note basenames (stem only, no extension) in the vault.
Use Levenshtein distance: if the best match has ratio ≥ 0.85, propose:
```
[[X]]  →  [[actual/path/best-match]]
```
Collect all proposed renames into a triage table.

**Bucket 2 — Stub needed:**
If `X` appears ≥3 times across different vault files AND no fuzzy match with ratio ≥0.85 exists, mark it as a stub candidate. These will be appended to `wiki/gaps.md` under `## Stub Pages (need creation)` with occurrence count:
```
- [ ] `[[X]]` — mentioned N times; no note exists yet
```

**Bucket 3 — Drop:**
If `X` appears only once vault-wide and no fuzzy match exists, propose removing just the wikilink brackets (keep surrounding prose). Example: `See [[X]] for details` → `See X for details`.

**Output:** Write `wiki/dangling-YYYY-MM-DD.md` with a triage table:
```markdown
| Wikilink | Occurrences | Bucket | Proposed action |
|---|---|---|---|
| [[old-note-name]] | 5 | rename | → [[learning/langgraph/renamed-note]] |
| [[milvus-deployment]] | 7 | stub | add to gaps.md |
| [[some-dead-link]] | 1 | drop | remove brackets |
```

**Execution (Phase 3):** On confirmation:
1. Apply renames: use `sed`/Edit to replace `[[X]]` → `[[Y]]` in all files that contain the link.
2. Append stub candidates to `wiki/gaps.md` under `## Stub Pages (need creation)`.
3. Apply drops: remove brackets only, keep prose text.
4. Log: "Dangling-link triage: N renamed, M stubs added to gaps, K dropped."

**2c. Orphan pages**
For each page in `research/`, `learning/`, `data-engineering/`, `projects/`:
- Grep the entire vault (excluding `wiki/index.md`, `wiki/routing/`, `wiki/log.md`) for `[[page-stem]]` or `[[folder/page-stem]]`
- Flag pages with zero inbound content wikilinks as orphans
- List up to 15 orphans with suggested cross-link targets (pages with similar tags)
- Do not check `attachments/` — image files are assets and are intentionally not cross-linked.

**2d. Concept stubs**
Scan all pages for proper noun / concept names (capitalized or quoted terms) that appear in prose 2+ times across multiple pages but have no dedicated wiki page.
List as candidates for new stub pages (e.g. "TemporalTables", "Milvus", "pgvector" appear in 3 pages but no `[[milvus]]` page exists).

**2e. Contradictions**
Use graph community files — do not read all vault notes.
For each community in `wiki/graph/nodes/`:
- Read the community `.json` file; compare `summary` and `tags` fields across members
- Identify pairs where summaries or tags suggest opposing claims about the same concept
- Only read the actual note files for flagged pairs (not all members)
Flag cases where two pages make opposing claims about the same concept (e.g. one recommends X, another recommends against X for the same use case).


**2e-ext2. Staleness scan (LLM Wiki v2)**
Read TTL rules from `{{VAULT}}/SCHEMA.md` (TTL Rules table).
For each `.md` file in `learning/`, `research/`, `wiki/`:
- Read frontmatter `last_verified` field (fall back to `updated`, then `created`)
- Determine topic class from `tags` to get TTL
- Flag files where `today - last_verified > TTL` as overdue
Sort by most overdue first. Report format:
```
| Note | Tags | last_verified | TTL | Days overdue |
```
Group by topic class. Suggest using `/refresh <note>` to re-verify.

**2e-ext3. Frontmatter schema validator**
Canonical fields from `SCHEMA.md`: `title`, `created`, `updated`, `last_verified`, `confidence`, `provenance`, `maturity`, `tags`, `type`, `source`, `related`
For each page, flag:
- Missing `title` (note: `title` may be set or derived from first `# Heading`)
- `date` field present instead of `created` (needs migration — run `migrate_frontmatter.py`)
- Missing `type` field
- `related` field completely absent (vs `related: []` which is fine)
- Missing `last_verified` field (new requirement — default to `created` date)
- Missing `confidence` field (new requirement)
- Missing `provenance` field (new requirement)
- Missing `maturity` field (new requirement — default to `seedling`)
Summarise as: "N pages need frontmatter migration" with a suggestion to run `python {{SCRIPTS}}/migrate_frontmatter.py --write`

**2e-ext3b. Maturity distribution**
For all notes with a `maturity:` field, count by value (`seedling` / `budding` / `evergreen`).
Report as a table:
```
| Maturity    | Count | % of vault |
|-------------|-------|------------|
| evergreen   |     N |        X%  |
| budding     |     N |        X%  |
| seedling    |     N |        X%  |
| missing     |     N |        X%  |
```
Flag all notes with `maturity: budding` or `maturity: evergreen` that are missing a `## Recall prompts` section — these are candidates for retrieval prompt backfill via `/uplift`.

**2e-ext4. Version-pin scan**
In `learning/*/production.md` and `learning/*/cookbook.md` files:
- Grep for fenced code blocks that lack a `# tested: <lib>==<version>` comment in the first 3 lines
- List unpinned blocks as: file | block line number | suggested pin format
This helps catch snippets that may become stale without a version marker.

**2e-ext5. v2 Quality Score + Typed Rubric (lint.py)**
Run `python {{SCRIPTS}}/lint.py --typed` to produce both reports:
- `wiki/lint-YYYY-MM-DD.md` — flat v2 leaderboard (0–7 per note; hub notes excluded from flat scoring)
- `wiki/lint-typed-YYYY-MM-DD.md` — typed rubric coverage: U1 (declarative title %), U3 (atomic %), U4 (retrieval prompts %), U7 (maturity %), plus maturity distribution, U4 gap queue, and hub inventory

Report the per-folder flat average and the U4/U7 gaps in the Phase 2 report. Do NOT open raw output files — run the script and read the first 100 lines of each.

Note: Hub notes (`type: index`) are **excluded** from flat scoring and appear in the dedicated hub table in the typed report. For hub quality scoring use the 6-dimension 0–12 rubric from `wiki/audit-hubs-2026-05-16.md`.

**2e-ext5b. Retrieval prompt gap scan**
Grep all `.md` files in `learning/` and `data-engineering/` for the string `## Recall prompts`.
Report:
- Total notes scanned
- Notes WITH retrieval prompts (count + list)
- Notes WITHOUT retrieval prompts that have `maturity: budding` or `maturity: evergreen` — these are the priority backfill queue
Suggest: "Run `/uplift --worst N` to add retrieval prompts to the N highest-priority notes."

**2e-ext6. Learning folder structure check**
Read `{{VAULT}}/learning/CONVENTIONS.md` for the three-tier policy.
For each runtime-tier folder (langgraph, langchain, google-adk, rag, fastapi, vector-db, llm-infra, agents):
- Check presence of: `index.md`, `production.md`, `cookbook.md`
- Report missing required files: "langgraph is missing: production.md, cookbook.md"
For each folder in `learning/`:
- Check that `index.md` exists; flag missing ones
- Check that no file is named `00-*.md` or uses Title-Case (except inside course subfolders with numbered notes)

**2e-ext7. Cluster integrity check**
For Obsidian graph clustering: each leaf note should link back to its folder hub, and each hub should list all its leaves.

For each leaf note in `learning/<topic>/*.md` (excluding `index.md`, `production.md`, `cookbook.md`):
- Check for presence of `**Up:** [[learning/<topic>/index]]` line in the note body
- Flag leaves missing this Up-link

For each folder with an `index.md` in `learning/`:
- List all `.md` files in that folder (and immediate subfolders for multi-level courses)
- Check that each leaf is linked from `index.md`
- Flag leaves not listed in their hub

Report format:
```
Cluster integrity issues:
- Leaves missing Up-link: N (list paths)
- Leaves not in hub index: N (list paths + which hub)
```


**2f. Actionable next research**
From `## Open Questions` sections across all pages + concept stubs + gaps, produce 3–5 specific research topics with actionable web search queries:
- Topic: "X"
- Search: `"X" site:relevant-domain.com OR "X" <qualifier>`

---

## Phase 2: Report

Show the consolidated report before touching anything:

```
## Vault Lint — YYYY-MM-DD

### File System Issues
**Loose root files:** [list or "none"]
**Inbox items:** [list or "none"]
**Misplaced files:** [file → suggested folder]
**Duplicate files:** [pairs]
**Empty folders:** [list or "none"]
**Junk files:** [list or "none"]
**Master summaries to consolidate:** [list]

### Wiki Health
**Not in index (N pages):** [list]
**Broken wikilinks (N):** [[link]] in file.md
**Dangling-link triage:** N renames proposed, M stubs to add to gaps, K drops proposed → see `wiki/dangling-YYYY-MM-DD.md`
**Orphan pages (N):** [list with suggested cross-link targets]
**Stale notes (N overdue by TTL class):** [table: note | last_verified | TTL | days overdue]
**Missing frontmatter fields (N pages):** [summary + migration command if applicable]
**Missing `maturity:` field (N pages):** [list — default to seedling]
**Maturity distribution:** seedling N | budding N | evergreen N | missing N
**Notes missing retrieval prompts (budding/evergreen only, N):** [list — priority backfill queue for /uplift]
**Unpinned code blocks (N):** [file | line | suggested fix]
**Missing required learning files (N):** [folder | missing files]
**Concept stubs to create (N):** [list]
**Contradictions (N):** [description]

### Suggested Next Research
1. Topic: "..." | Search: "..."
2. Topic: "..." | Search: "..."
3. Topic: "..." | Search: "..."

### Summary
X files to move | X to delete | X to index | X links to fix | X stubs to create
```

Ask: **"Fix all? Or tell me what to skip."**

---

## Phase 3: Execute

Act on user approval:

- **Move** misplaced files to correct folders (`mv`)
- **Delete** junk files (`rm`)
- **Consolidate** master summaries → `archive/outputs/master-summary.md` → delete originals
- **Add** missing entries to `wiki/index.md`
- **Fix** broken wikilinks (update path if renamed, remove if target never existed)
- **Write** `wiki/lint-YYYY-MM-DD.md` with the full report
- **Manage `wiki/gaps.md`** (see section below)
- **Append** to `wiki/log.md`:

```
## [DATE] lint | Vault Health Check
- File system: X moved, Y deleted, Z consolidated
- Wiki: N index entries added, M links fixed
- Concept stubs identified: [[concept-a]], [[concept-b]]
- Contradictions flagged: N
- Gaps: [archived old gaps.md | created new gaps.md with N items | no change]
- Report: [[wiki/lint-YYYY-MM-DD]]
```

Never delete `.md` content files without explicit user confirmation per file. Do not touch `.obsidian/` or `.env`.

---

## Gaps Lifecycle

`wiki/gaps.md` tracks open research backlog. Manage it as part of every lint run:

### Step A — Archive completed gaps
Read `wiki/gaps.md` (if it exists).
Count unchecked items (`- [ ]`). Count checked items (`- [x]`).

- **All items checked (100% complete):** Move `wiki/gaps.md` → `archive/gaps-YYYY-MM-DD.md` (use today's date). Do not delete — preserve as archive. Log: "Archived completed gaps.md → archive/gaps-YYYY-MM-DD.md".
- **Some items unchecked:** Leave the file in place. Do not archive.
- **File does not exist:** Skip archive step.

### Step B — Create new gaps.md (if needed)
After archiving (or if no gaps.md exists), collect new gaps found during this lint run:

From **2d (Concept stubs):** list all newly identified stub candidates.
From **2f (Actionable next research):** list open questions not yet answered.
From **2b/2c (Broken links / orphans):** note any that represent knowledge gaps rather than just link issues.

If new gaps were found:
- Write `wiki/gaps.md` with frontmatter and dated header:

```markdown
---
title: Wiki Gaps — Research Backlog
date: YYYY-MM-DD
tags: [gaps, backlog, meta]
type: meta
---

# Wiki Gaps — Research Backlog

Identified by `/lint` on YYYY-MM-DD. Work through these with `/ingest <topic>`.

---

## Stub Pages (need expansion)

- [ ] `[[path/page]]` — brief description of what's missing

---

## Open Questions

### Topic
- [ ] Question → context

---

## Missing Concept Pages

### Category
- [ ] **ConceptName** — why it matters / where it was referenced
```

- Add entry to `wiki/index.md` under Meta section if not already present: `- [[wiki/gaps]] — Research backlog and open questions`
- Log: "Created new gaps.md with N items"

If no new gaps were found: do not create `wiki/gaps.md`. Log: "No new gaps identified".

---

## Quarterly Mode (--quarterly flag only)

Run these extra steps after Phase 1-3, then write `wiki/audit-YYYY-Q<N>.md` instead of `wiki/lint-YYYY-MM-DD.md`.

**Q1. Determine quarter**
Label the report `YYYY-Q<N>` from today's date. Check if `wiki/audit-YYYY-Q<N>.md` already exists → ask "overwrite or append?"

**Q2. Confidence scan**
Count notes in `learning/` and `research/` by `confidence:` value:
- `high` / `medium` / `low` / missing field
List all `confidence: low` notes — these are the highest-risk knowledge.

**Q3. Write quarterly report** to `wiki/audit-YYYY-Q<N>.md`:

```markdown
---
title: Vault Audit — YYYY-Q<N>
created: <TODAY>
updated: <TODAY>
type: meta
---

# Vault Audit — YYYY-Q<N>

## Summary
- Total notes: N | Overdue: N (X%) | Low/missing confidence: N
- Contradictions: N | Orphans: N | Dangling links: N

## Priority Actions
1. /refresh the N most overdue: [[note1]], [[note2]]
2. Backfill confidence on N notes
3. Resolve contradictions: ...

## Staleness Detail
[from 2e-ext2]

## Confidence Distribution
[from Q2]

## Contradictions
[from 2e]

## Orphans & Dangling Links
[from 2c + 2b-triage]

## Learning Folder Gaps
[from 2e-ext6]
```

**Q4. Log entry:**
```
## [DATE] audit | Quarterly vault health — YYYY-Q<N>
- Report: [[wiki/audit-YYYY-Q<N>]]
- Overdue: N | Low confidence: N | Contradictions: N | Orphans: N
```
