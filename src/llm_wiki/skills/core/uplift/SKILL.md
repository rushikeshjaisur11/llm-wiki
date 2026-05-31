---
name: uplift
description: Bulk-fix low-scoring vault notes. Generates missing quality-rubric fields (tldr-callout, diagram, worked-example, when-not-to-use, see-also, version-pins, retrieval-prompts) using langchain/langgraph notes as gold templates. Promotes maturity tag. Raises every folder to ≥6/7 average score.
---

# Uplift — Bulk Note Quality Fix

Vault root: `{{VAULT}}/`
Quality rubric canonical source: `{{VAULT}}/SCHEMA.md` § Typed Rubric v3
Gold-standard templates: `learning/langgraph/index.md`, `learning/langchain/01-*.md`, `learning/google-adk/index.md` (all 7/7)

---

## Argument parsing

| Argument | Behaviour |
|---|---|
| `/uplift <folder>` | Process all notes in `learning/<folder>/` (or `data-engineering/<folder>/`) that score <7 on flat v2 OR are missing U4/U7 |
| `/uplift <note-path>` | Process a single note at `<note-path>` |
| `/uplift --worst N` | Identify the N lowest-scoring notes vault-wide (flat v2) and process them |
| `/uplift --worst-typed N` | Identify the N notes most deficient on typed rubric (missing U4 first, then U7) and process them. Run this for the bulk recall-prompt + maturity backfill campaign. |
| `/uplift` (no arg) | Ask: "Uplift a specific folder, a single note, or the N worst notes?" |

---

## Step 1: Determine work queue

1. Find the latest lint reports:
   - Flat: `Glob wiki/lint-[0-9]*.md` → sort descending → read first result.
   - Typed: `Glob wiki/lint-typed-*.md` → sort descending → read first result (may not exist yet).
2. Check report dates. If flat report is older than 1 day, say:
   > "The latest lint report is from `<date>`. Running a fresh lint scan before uplifting…"
   Run: `python {{SCRIPTS}}/lint.py --typed`
   This produces both `wiki/lint-<TODAY>.md` and `wiki/lint-typed-<TODAY>.md`.
3. Parse the report(s) for the target scope:
   - For `/uplift <folder>`: extract notes in that folder with flat score < 7 **OR** missing U4/U7 per the typed report.
   - For `/uplift <note-path>`: read the specific note.
   - For `/uplift --worst N`: take the N lowest flat-score notes.
   - For `/uplift --worst-typed N`: take the N notes most deficient on typed rubric — sort by:
     1. Missing U4 (recall prompts) — highest priority
     2. Missing U7 (maturity) — second priority
     3. Missing U1 (declarative title) — third priority
     Order within each tier by folder (alphabetical) so the backfill is folder-contiguous.
4. Print the work queue as a table:

   | Note | Flat score | U4 recall | U7 maturity | Action |
   |---|---|---|---|---|
   | `dsa/06-dynamic-programming.md` | 7/7 | ✗ | ✗ | add recall prompts + set maturity |
   | `sql/02-window-functions.md` | 7/7 | ✗ | budding | add recall prompts |
   | … | … | … | … | … |

   Ask: "Proceed with uplifting these **N notes**?"

---

## Step 2: Generate missing blocks (per note)

For each note in the work queue:

### 2a. Read the note
Read the full note. Also read the highest-scoring note in the same folder (from lint data) as a structural reference. If folder has no 6+ note, use `learning/langgraph/index.md` as the gold template.

### 2b. Generate only the missing fields

**tldr-callout** (if missing):
- Read the note body; identify the core topic, the reason it matters, and the key insight.
- Write a 3-line (max) `> [!tldr]` Obsidian callout. Format:
  ```markdown
  > [!tldr]
  > **What:** <one sentence — what this note covers>
  > **Why:** <one sentence — why this matters in practice>
  > **Key insight:** <one sentence — the most surprising or non-obvious claim, with a number if available>
  ```
- Placement: immediately after the `# Title` line, before any other content.

**diagram** (if missing):
- Scan the note for: processes, pipelines, architectures, sequential steps, decision points, component relationships.
- Choose diagram type:
  - Multi-step pipeline or flow → `flowchart LR`
  - Decision "use X when Y" → `flowchart TD`
  - Message exchange between systems → `sequenceDiagram`
  - Numeric distributions / benchmarks → `xychart-beta`
  - Architecture with subsystems → `flowchart LR` with subgraphs
- Color code: red = error/critical, orange = warning, green = recommended, blue = informational.
- Placement: inside the most relevant section (usually `## How It Works` or first conceptual section). Create the section if absent.

**worked-example** (if missing):
- Pull a concrete example from the note's existing content (real numbers the source provided). If none exist, synthesize a plausible realistic example (e.g. dataset sizes in GB/TB, latency in ms, row counts in millions).
- Never use `<placeholder>`, `<your-value>`, or `TODO`.
- Write as an `> [!example]` callout with a title. Format:
  ```markdown
  > [!example] <Short title describing the example>
  > **Input:** <concrete value>  
  > **Process:** <what happens>  
  > **Output:** <concrete result>
  ```
- Placement: after the first conceptual explanation or in `## How It Works`.

**when-not-to-use** (if missing):
- Read the note for scope limitations, caveats, tradeoffs, and anti-patterns.
- Write 3–5 bulleted anti-patterns. Format:
  ```markdown
  ## When NOT to Use
  - ❌ <anti-pattern 1> — <one-line reason>
  - ❌ <anti-pattern 2> — <one-line reason>
  - ❌ <anti-pattern 3> — <one-line reason>
  ```
- Placement: after the last concept section, before See Also.

**see-also** (if missing):
- Run embedding search to find real vault links:
  ```
  python {{SCRIPTS}}/search.py "<note title and tags>" --top 8
  ```
  Pick 3–5 most relevant results. Do NOT invent links — only use paths returned by the search.
  If search unavailable, read `wiki/index.md` and pick links manually by topic relevance.
- Write as:
  ```markdown
  ## See Also
  - [[learning/related-note-1]] — one-line context
  - [[learning/related-note-2]] — one-line context
  ```
- Placement: last section in the note.

**version-pins** (only for `production.md` and `cookbook.md`, if missing):
- Scan all fenced code blocks (` ``` `) in the note.
- For each block missing a `# tested:` first line:
  - Identify the primary library from import statements or function names.
  - If version is detectable from note content, use it.
  - If version is not detectable, ask: "Code block in `<note>` uses `<library>` — what version was this tested against?"
  - Add `# tested: <lib>==<version>, python==3.12` as the first line of the block.

**retrieval-prompts** (if missing — applies to ALL leaf types: `learning`, `cookbook`, `production`, `cheatsheet`, `comparison`, `troubleshooting`):
- Read the note body. Focus on: key thresholds/numbers, API names, decision criteria, failure modes, "when NOT to use" anti-patterns.
- Write a `## Recall prompts` section using Obsidian collapsible callouts. Place it as the second-to-last section (before See Also).
- Format:
  ```markdown
  ## Recall prompts

  > [!question] <one specific retrievable fact — a mechanism, threshold, or decision>
  > [!answer]- <concrete answer — numbers, names, conditions; no vague generalities>

  > [!question] When would you NOT use <X>?
  > [!answer]- <specific anti-pattern with concrete triggering condition>
  ```
- Prompt count by maturity:
  - `seedling` → 2 prompts (the most critical fact + the key anti-pattern)
  - `budding` → 3 prompts
  - `evergreen` or promoting to evergreen → 4–5 prompts
- Skip only `type: index` hub notes and `type: reference` roadmaps (these are navigational, not retrievable facts).
- Skip `type: meta` (vault infra files — SCHEMA, CONVENTIONS, etc.).
- Quality bar: each answer must be a concrete fact (number, API name, failure mode) — not a restatement of the question. "Use buffered channels when goroutines produce faster than they consume" ✓. "Use it when needed" ✗.

### 2c. Merge changes into the note

Apply all generated blocks into the existing note at the correct positions. Never delete or rewrite existing content — only insert new sections/blocks.

Bump frontmatter and promote maturity:
```yaml
updated: <TODAY>
last_verified: <TODAY>
```

**Maturity promotion / backfill logic (runs on every uplift, even if no other fields were added):**
- Check current `maturity:` value; if field is missing, infer it first, then write it.
- Inference rules (in order — use the highest that all criteria are met):
  1. `evergreen`: all of [tldr-callout ✓, diagram/worked-example ✓, see-also ✓, recall prompts (U4) ✓, last_verified within TTL ✓, confidence: high ✓]
  2. `budding`: all of [tldr-callout ✓, diagram OR worked-example ✓, see-also ✓] — but recall prompts may still be missing
  3. `seedling`: everything else (newly created, stub content, missing fields)
- If existing `maturity:` is lower than the inferred value, **promote** it (e.g., seedling → budding).
- Never demote (do not lower maturity on uplift — only `/refresh` can do that when `last_verified` lapses).
- When running `--worst-typed` for the bulk backfill, **always write `maturity:` even when no other field changes** — this is a valid single-field uplift.

---

## Step 3: Show diff and confirm

After generating all missing blocks for the current folder (or batch), show a summary:

> **Uplift preview — `learning/python/` (5 notes)**
>
> | Note | Before | After | Fields added |
> |---|---|---|---|
> | `python/index.md` | 3/7 | 6/7 | tldr-callout, diagram, worked-example, when-not-to-use |
> | `python/pydantic/05-additional-field-features.md` | 3/7 | 6/7 | tldr-callout, diagram, when-not-to-use |
> | … | … | … | … |
>
> Apply these changes?

Wait for confirmation before writing. If the user asks to review individual notes, show the generated additions for that note and wait for approval before including it.

---

## Step 4: Write and log

On confirmation:
1. Write each modified note using the Edit tool (targeted inserts — not full rewrites).
2. Append to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] uplift | <scope>
   - Scope: <folder | note-path | --worst N>
   - Notes processed: N
   - Before avg score: X.X/7
   - After avg score: Y.Y/7
   - Fields generated: <list of unique field types added>
   ```

---

## Step 5: Suggest next run

After completing, suggest:
> "Run `/lint --typed` to get updated scores and typed coverage, or `/uplift <next-folder>` to continue."

Print two tables:
1. Folders still below 6/7 flat average (from flat lint report) — sorted ascending.
2. Folders still below 80% U4 coverage (from typed lint report) — sorted ascending by U4 %. Suffix the U4 gap count: "X notes still missing recall prompts".
