---
name: lint
description: Full vault health-check — scans for file system issues (misplaced files, junk, duplicates, unprocessed inbox) and wiki knowledge issues (orphan pages, broken wikilinks, concept stubs, contradictions). Reports first, executes after confirmation. Replaces /organize-vault.
---

# Lint — Full Vault Health Check

## Phase 1: Scan (read-only)

### File System Health

**1a. Loose root files**
Files at vault root other than `CLAUDE.md`, `memory.md`, `wiki/` — flag these.

**1b. Unprocessed inbox/**
`Glob inbox/*` — list all files. These are awaiting `/ingest`.

**1c. Duplicate files**
Files with the same name but different casing, or very similar names in the same folder.

**1d. Misplaced files**
Check each file's content against the folder rules in CLAUDE.md. Flag files in the wrong folder.

**1e. Empty or near-empty folders**
Folders with 0 or 1 file — flag for review.

**1f. Junk file types**
`.tmp`, `.bak`, `.DS_Store`, `desktop.ini`, `Thumbs.db`, `.pdf` outside `inbox/` or `sources/`

**1g. Scattered outputs**
Find all `MASTER_SUMMARY.md` / `master-summary*.md` files across `outputs/`.
Plan: consolidate into `archive/outputs/master-summary.md`, delete originals.

---

### Wiki Knowledge Health

**2a. Not in index**
Compare all `.md` files in knowledge folders against `wiki/index.md`. List pages missing from the index.

**2b. Broken wikilinks**
Read `vault-tool` from CLAUDE.md. Branch:

**If vault-tool = obsidian:**
Run: `obsidian unresolved verbose`
This returns all unresolved links with the files that contain them.
If Obsidian is not running, fall back to Grep method below.

**All other vaults (or Obsidian fallback):**
Grep for all `[[link]]` patterns: `grep -roh "\[\[.*?\]\]" <vault-root> --include="*.md"`
For each link, strip `[[` `]]` and check if the target file exists. List broken ones with the containing file.

**2c. Orphan pages**
Read `vault-tool` from CLAUDE.md. Branch:

**If vault-tool = obsidian:**
Use obsidian-cli (most accurate — handles aliases and renamed files):
`obsidian backlinks file="<note-name>"`
If Obsidian is not running, fall back to Grep method below.

**All other vaults (or Obsidian fallback):**
For each `.md` file, get the stem (filename without `.md`).
Run: `grep -rl "\[\[<stem>\]\]" <vault-root> --include="*.md"`
If no results besides the file itself → orphan.

**2d. Concept stubs**
Scan all pages for concept names appearing in prose 2+ times across multiple pages but lacking their own wiki page. List as candidates for new pages.

**2e. Contradictions**
Scan pages that share topic tags for opposing claims about the same concept.

**2f. Actionable next research**
From `## Open Questions` sections + concept stubs + gaps, produce 3–5 specific research topics with search queries:
- Topic: "X"
- Search: `"X" <qualifier>`

---

## Phase 2: Report

```
## Vault Lint — YYYY-MM-DD

### File System Issues
**Loose root files:** ...
**Inbox items:** ...
**Misplaced files:** ...
**Junk files:** ...
**Outputs to consolidate:** ...

### Wiki Health
**Not in index (N):** ...
**Broken wikilinks (N):** ...
**Orphan pages (N):** ...
**Concept stubs (N):** ...
**Contradictions (N):** ...

### Suggested Next Research
1. Topic: "..." | Search: "..."

### Summary
X files to move | X to delete | X to index | X links to fix | X stubs to create
```

Ask: **"Fix all? Or tell me what to skip."**

---

## Phase 3: Execute

- **Move** misplaced files to correct folders
- **Delete** junk files
- **Consolidate** master summaries → `archive/outputs/master-summary.md`
- **Add** missing entries to `wiki/index.md`
- **Fix** or remove broken wikilinks
- **Write** `wiki/lint-YYYY-MM-DD.md` with full report
- **Append** to `wiki/log.md`:
  ```
  ## [DATE] lint | Vault Health Check
  - File system: X moved, Y deleted
  - Wiki: N index entries added, M links fixed
  - Concept stubs: [[concept-a]], [[concept-b]]
  - Report: [[wiki/lint-YYYY-MM-DD]]
  ```

Never delete `.md` content files without explicit per-file confirmation. Do not touch `.obsidian/` or `.env`.
