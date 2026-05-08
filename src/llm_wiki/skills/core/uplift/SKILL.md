---
name: uplift
description: Bulk-fix low-scoring vault notes. Generates missing quality-rubric fields (tldr-callout, diagram, worked-example, when-not-to-use, see-also, version-pins) using langchain/langgraph notes as gold templates. Raises every folder to ≥6/7 average score.
---

# Uplift — Bulk Note Quality Fix

Vault root: `c:/Users/rushi/llm-wiki-memory/`
Quality rubric canonical source: `c:/Users/rushi/llm-wiki-memory/SCHEMA.md` § Quality Rubric v2
Gold-standard templates: `learning/langgraph/index.md`, `learning/langchain/01-*.md`, `learning/google-adk/index.md` (all 7/7)

---

## Argument parsing

| Argument | Behaviour |
|---|---|
| `/uplift <folder>` | Process all notes in `learning/<folder>/` (or `data-engineering/<folder>/`) that score <7 |
| `/uplift <note-path>` | Process a single note at `<note-path>` |
| `/uplift --worst N` | Identify the N lowest-scoring notes vault-wide and process them |
| `/uplift` (no arg) | Ask: "Uplift a specific folder, a single note, or the N worst notes?" |

---

## Step 1: Determine work queue

1. Find the latest lint report: `Glob wiki/lint-*.md` → sort by name descending → read the first result.
2. Check the date in the filename. If older than 1 day, say:
   > "The latest lint report is from `<date>`. Running a fresh lint scan before uplifting…"
   Then execute **only** the lint scan phase of `/lint` (Phase 1 + Phase 2 quality checks — no file system changes). This produces an updated `wiki/lint-<TODAY>.md`.
3. Parse the lint report for the target scope:
   - For `/uplift <folder>`: extract all notes in that folder with score < 7
   - For `/uplift <note-path>`: read the specific note entry
   - For `/uplift --worst N`: take the N lowest-scoring notes across all folders
4. Print the work queue as a table:

   | Note | Current score | Missing fields |
   |---|---|---|
   | `python/index.md` | 3/7 | tldr-callout, diagram, worked-example, when-not-to-use |
   | … | … | … |

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
  python C:/Users/rushi/.claude/skills/_wiki/search.py "<note title and tags>" --top 8
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

### 2c. Merge changes into the note

Apply all generated blocks into the existing note at the correct positions. Never delete or rewrite existing content — only insert new sections/blocks.

Bump frontmatter:
```yaml
updated: <TODAY>
last_verified: <TODAY>
```

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
> "Run `/lint` to get the updated scores, or `/uplift <next-folder>` to continue."

Print the folders still below 6/7 average (from the lint report) sorted by current average score ascending.
