---
name: tip
description: Write today's "note of the day" — pick a fresh, timely, non-duplicate topic (either from the tracked AI/LLM space — Claude/Claude Code workflow, LangGraph, LangChain, Google ADK, RAG, agents, vector DBs, new model/framework releases — or from whatever the vault's learning/ tree shows the user is actually studying, e.g. Python asyncio internals, new stdlib features, notable PEPs), research it, and file a rubric-compliant note into tips/ at the vault root. Runs manually or via the daily automation. Usage: /tip | /tip <optional topic hint> | /tip --digest (weekly roundup mode).
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

1. **See what's already covered.** Read `{{VAULT}}/tips/index.md`. If `{{VAULT}}/tips/`
   or `index.md` doesn't exist yet, this is the first run — treat it as "no topics covered
   yet" and continue (the folder and index get created in step 4, not as an error). Note the
   last ~30 days of topics; never repeat one of them.

2. **Pick a fresh topic.**
   - If a topic hint was given as an argument, use it.
   - Otherwise survey two candidate spaces before picking:
     1. **What the user is actually learning** — scan the top-level folders/tags under
        `{{VAULT}}/learning/` (e.g. a `learning/python/` folder is a signal to look for new or
        interesting Python concepts: `asyncio` internals, new stdlib features, notable PEPs,
        etc.). Prefer topics that go a level deeper than what's already there instead of
        restating existing notes.
     2. **The tracked AI/LLM space** — `WebSearch` for what's genuinely new or notable in the
        last ~2 weeks: Claude / Claude Code releases & workflow tips, LangGraph, LangChain,
        Google ADK, RAG techniques, agent frameworks, vector DBs, and any other notable AI/LLM
        framework, model, or paper release. Prefer primary sources (official docs/blogs/release
        notes) over aggregator summaries.
   - Dedup check:
     ```
     python {{SCRIPTS}}/search.py "<candidate topic>" --top 5
     ```
     If the vault already has solid coverage, pick the next candidate.

3. **Write the note** → `{{VAULT}}/tips/<TODAY>-<slug>.md`. Follow
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

   > **Up:** [[tips/index]]

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
   > <!-- required whenever the topic is a language/library: runnable code (not prose),
   >      concrete numbers, or a CLI command — no placeholders -->

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

4. **Update the tips hub** `{{VAULT}}/tips/index.md`:
   - If `{{VAULT}}/tips/` doesn't exist, create the folder — this is expected on the first run,
     not a failure.
   - If `index.md` is missing, create it (`type: index`, one-paragraph orientation, this section):
     ```markdown
     ## Tips log
     ```
   - Prepend a line under `## Tips log`:
     ```
     - <TODAY> — [[tips/<TODAY>-<slug>|<Title>]]
     ```

5. → **[Wiki Update]** (below).

---

## Digest mode (`--digest`)

Used by the weekly automation. Does not research a new topic — synthesizes the past week's
tips into one roundup note.

1. Read every file in `{{VAULT}}/tips/` dated in the last 7 days (from `index.md`'s
   log or by filename date). If `{{VAULT}}/tips/` or `index.md` doesn't exist, or no files
   match, stop and report "no tips this week" — this is a normal empty state, not an error.
2. Write `{{VAULT}}/tips/weekly/<ISO-week>-digest.md` (e.g. `2026-W27-digest.md`),
   same frontmatter shape as Tip mode (`type: changelog`, `tags: [tips, weekly-digest]`), body:
   - `> [!tldr]` — the week's themes in 2-3 lines
   - `## This Week` — one bullet per tip note with a wikilink and one-line takeaway
   - `## Notable Releases` — anything release/version-worthy from the week, if applicable
   - `## See Also` — link back to `[[tips/index]]` and prior weekly digests
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
   - [[tips/<file>]] — one-line summary (<TODAY>)
   ```
3. Append to `wiki/log.md`:
   ```
   ## [DATE] tip | <Title>
   - Note: [[tips/<file>]]
   - Mode: <tip | weekly-digest>
   - Skills_touched: [tip]
   ```
4. Update search indexes:
   ```
   python {{SCRIPTS}}/build_graph.py --update tips/<file>.md
   python {{SCRIPTS}}/build_routing.py --update tips/<file>.md
   python {{SCRIPTS}}/build_index.py --update tips/<file>.md
   python {{SCRIPTS}}/build_embeddings.py --update tips/<file>.md
   ```
   If scripts aren't found or `wiki/graph.json` doesn't exist, skip — the next `/daily` will
   nudge a full `/graphbuild` instead (this keeps unattended cron runs from failing on a
   missing index).
