---
name: tip
description: Write today's AI/LLM "note of the day" — pick a fresh, timely, non-duplicate topic (Claude/Claude Code workflow, LangGraph, LangChain, Google ADK, RAG, agents, vector DBs, new model/framework releases), research it, and file a rubric-compliant note into learning/tips/. Runs manually or via the daily automation. Usage: /tip | /tip <optional topic hint> | /tip --digest (weekly roundup mode).
---

Vault root: `{{VAULT}}/`

## Mode detection

| Input | Mode |
|---|---|
| `--digest` | Weekly digest — see **Digest mode** below |
| topic hint text | Tip mode, using the hint as the topic instead of auto-picking |
| no argument | Tip mode, auto-pick a topic |

---

## Tip mode (default)

1. **See what's already covered.** Read `{{VAULT}}/learning/tips/index.md` (create it — see
   step 3 — if this is the first run). Note the last ~30 days of topics; never repeat one of
   them.

2. **Pick a fresh topic.**
   - If a topic hint was given as an argument, use it.
   - Otherwise `WebSearch` across the tracked space for what's genuinely new or notable in
     the last ~2 weeks: Claude / Claude Code releases & workflow tips, LangGraph, LangChain,
     Google ADK, RAG techniques, agent frameworks, vector DBs, and any other notable AI/LLM
     framework, model, or paper release. Prefer primary sources (official docs/blogs/release
     notes) over aggregator summaries.
   - Dedup check:
     ```
     python {{SCRIPTS}}/search.py "<candidate topic>" --top 5
     ```
     If the vault already has solid coverage, pick the next candidate.

3. **Write the note** → `{{VAULT}}/learning/tips/<TODAY>-<slug>.md`. Follow
   `{{VAULT}}/SCHEMA.md` in full (required frontmatter + Typed Rubric U1–U7):

   ```markdown
   ---
   title: <Declarative title — Topic: Specific Claim (U1)>
   created: <TODAY>
   updated: <TODAY>
   last_verified: <TODAY>
   confidence: high
   provenance: extracted
   maturity: seedling
   tags:
   - tips
   - <topic-tag>
   type: learning
   source: <primary URL(s) found>
   related: []
   ---

   # <Title>

   > **Up:** [[learning/tips/index]]

   > [!tldr]
   > <2-3 lines, in your own words — what changed / what it is / why it matters>

   ---

   ## What's New

   <!-- 3-5 sentences: the concrete update, release, or best-practice being covered -->

   ```mermaid
   flowchart LR
       A[Before] --> B[Change] --> C[After]
   ```

   > [!example] Worked example
   > <!-- concrete numbers, a CLI command, or a code snippet — no placeholders -->

   ---

   ## When Not To Use / Anti-pattern

   <!-- one concrete condition where this doesn't apply -->

   ---

   ## Recall prompts

   > [!question] <one specific retrievable fact>

   > [!answer]- <concrete answer>

   > [!question] When would you NOT use this?

   > [!answer]- <specific anti-pattern>

   ---

   ## See Also
   <!-- 3-5 wikilinks -->
   ```

   Apply the vault's **anonymization rule** (no employer names) from `{{VAULT}}/CLAUDE.md`.

4. **Update the tips hub** `{{VAULT}}/learning/tips/index.md`:
   - If missing, create it (`type: index`, one-paragraph orientation, this section):
     ```markdown
     ## Tips log
     ```
   - Prepend a line under `## Tips log`:
     ```
     - <TODAY> — [[learning/tips/<TODAY>-<slug>|<Title>]]
     ```

5. → **[Wiki Update]** (below).

---

## Digest mode (`--digest`)

Used by the weekly automation. Does not research a new topic — synthesizes the past week's
tips into one roundup note.

1. Read every file in `{{VAULT}}/learning/tips/` dated in the last 7 days (from `index.md`'s
   log or by filename date). If none, stop and report "no tips this week."
2. Write `{{VAULT}}/learning/tips/weekly/<ISO-week>-digest.md` (e.g. `2026-W27-digest.md`),
   same frontmatter shape as Tip mode (`type: changelog`, `tags: [tips, weekly-digest]`), body:
   - `> [!tldr]` — the week's themes in 2-3 lines
   - `## This Week` — one bullet per tip note with a wikilink and one-line takeaway
   - `## Notable Releases` — anything release/version-worthy from the week, if applicable
   - `## See Also` — link back to `[[learning/tips/index]]` and prior weekly digests
3. Prepend the digest to the tips hub under a `## Weekly digests` section (create if missing).
4. → **[Wiki Update]** (below), using `weekly-digest` as the log's Mode field.

---

## Wiki Update (runs after every mode)

Same as `/ingest`'s Wiki Update tail:

1. ```
   python {{SCRIPTS}}/search.py "<new note tags and title keywords>" --top 8
   ```
   Cross-link the top matches under the note's `## See Also`.
2. Add an entry to `wiki/index.md`:
   ```
   - [[learning/tips/<file>]] — one-line summary (<TODAY>)
   ```
3. Append to `wiki/log.md`:
   ```
   ## [DATE] tip | <Title>
   - Note: [[learning/tips/<file>]]
   - Mode: <tip | weekly-digest>
   - Skills_touched: [tip]
   ```
4. Update search indexes:
   ```
   python {{SCRIPTS}}/build_graph.py --update learning/tips/<file>.md
   python {{SCRIPTS}}/build_routing.py --update learning/tips/<file>.md
   python {{SCRIPTS}}/build_index.py --update learning/tips/<file>.md
   python {{SCRIPTS}}/build_embeddings.py --update learning/tips/<file>.md
   ```
   If scripts aren't found or `wiki/graph.json` doesn't exist, skip — the next `/daily` will
   nudge a full `/graphbuild` instead (this keeps unattended cron runs from failing on a
   missing index).
