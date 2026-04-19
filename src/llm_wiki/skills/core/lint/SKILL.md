---
name: lint
description: Full vault health-check — scans for file system issues (misplaced files, junk, duplicates, unprocessed inbox) and wiki knowledge issues (orphan pages, broken wikilinks, concept stubs, contradictions). Reports first, executes after confirmation. Replaces /organize-vault.
---

# Lint — Full Vault Health Check

Vault root: `{{VAULT}}/`

## Phase 1: Scan (read-only)

### File System Health

**1a. Loose root files**
List all files at vault root other than: `CLAUDE.md`, `wiki/`
Flag: should only contain those plus folder structure and `.obsidian/`

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
  - `learning/fastapi/` — FastAPI course
  - `learning/git/` — Git notes
  - `learning/building-generative-ai-services/` — O'Reilly book notes
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
For each link, check the target file exists. List broken ones with the file that contains them.

**2c. Orphan pages**
Run `obsidian backlinks` for each page (or Grep for `[[page-name]]` occurrences across vault).
List pages with zero inbound links — they exist but nothing points to them.

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

**2e-ext. Orphan pages**
For each page in `research/`, `learning/`, `data-engineering/`, `projects/`:
- Grep the entire vault (excluding `wiki/index.md`, `wiki/routing/`, `wiki/log.md`) for `[[page-stem]]` or `[[folder/page-stem]]`
- Flag pages with zero inbound content wikilinks as orphans
- List up to 15 orphans with suggested cross-link targets (pages with similar tags)

**2e-ext2. Stale content detector**
For each page whose frontmatter `tags` contains any of: `llm`, `rag`, `framework`, `tooling`, `model-serving`, `claude-code`:
- Check `updated` field (or `created` if `updated` absent)
- Flag pages where that date is > 60 days before today as potentially stale
- List them with their date and a suggested web search query to verify currency

**2e-ext3. Frontmatter schema validator**
Canonical fields: `title`, `created`, `updated`, `tags`, `type`, `source`, `related`
For each page, flag:
- Missing `title` (note: `title` may be set or derived from first `# Heading`)
- `date` field present instead of `created` (needs migration — run `migrate_frontmatter.py`)
- Missing `type` field
- `related` field completely absent (vs `related: []` which is fine)
Summarise as: "N pages need frontmatter migration" with a suggestion to run `python {{SCRIPTS}}/migrate_frontmatter.py --write`

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
**Orphan pages (N):** [list with suggested cross-link targets]
**Stale content (N pages > 60 days old on fast-moving tags):** [list with dates]
**Frontmatter issues (N pages):** [summary + migration command if applicable]
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
