---
name: curriculum
description: |
  Goal-driven mastery curriculum generator. Researches a topic externally (web + library docs + vault), designs a comprehensive day-by-day roadmap, and generates concept notes + hands-on practicals + quiz/review files into curricula/ — one day at a time, on demand. Run once to get the full plan; run again per day to generate that day's material.
---

# /curriculum — Mastery Curriculum Generator

Vault root: `{{VAULT}}/`
Templates: `{{SKILLS}}/curriculum/templates/` — Read the relevant template file when generating day content or plan files.

---

## Invocation modes

| Command | Action |
|---------|--------|
| `/curriculum <goal>` | Research + generate full plan (first-time setup) |
| `/curriculum next` | Generate next undone day in the active curriculum |
| `/curriculum day <N>` | Generate (or regenerate) a specific day |
| `/curriculum list` | Show all curricula + progress summary |
| `/curriculum resume <slug>` | Switch active curriculum |
| `/curriculum audit <slug>` | Check concept coverage vs. generated days |
| `/curriculum replan` | Rewrite plan from next undone day (adaptive) |
| `/curriculum grade <N>` | Run grader for day N and append result to review |
| `/curriculum export <slug>` | Export shareable bundle (no personal progress) |
| `/curriculum import <path>` | Import a shared curriculum bundle |
| `/curriculum today` | Show/generate today's day based on schedule |
| `/curriculum ics [<slug>]` | Generate (or regenerate) schedule.ics for active or named curriculum |
| `/curriculum done <N>` | Quiz day N recall prompts; on pass archive files to done/ and tick all checkboxes |

Parse the first word after `/curriculum` to dispatch. If the argument is none of the keywords above, treat the entire argument string as a `<goal>` and run the first-time setup flow.

---

## FLOW A — First-time setup: `/curriculum <goal>`

### A1. Scope-setting questions

Before any research, ask with `AskUserQuestion` (all four in one call):

1. **Time budget** — "How many hours/day and how many total days? (e.g. 1.5 h/day for 60 days)"
2. **Starting level** — "Your current level relative to this goal?" (beginner / some-exposure / intermediate / advanced)
3. **Learning bias** — "Prefer concept-heavy, practical-heavy, or balanced?"
4. **Done means** — "What does finishing look like? (e.g. build a deployable project / pass interview / ship to production / general understanding)"

Store answers. If user skips a question, use: 1 h/day · 30 days · balanced · general-understanding.

### A2. Research phase (parallel — single message, multiple tool calls)

Derive `<YEAR>` from today's date (available in the session context) before running searches. Do not hardcode a year.

Fan out simultaneously:

**A2a. WebSearch** (run all three queries in parallel):
- `"<goal> curriculum <YEAR>"`
- `"<goal> complete roadmap beginner to advanced"`
- `"best resources to learn <goal> site:github.com OR site:reddit.com OR site:roadmap.sh"`

Additionally search for authoritative syllabi where applicable:
- deep learning / NLP / ML → search for fast.ai, DeepLearning.AI, Stanford CS229/CS224N
- data engineering → search for DataTalks.Club, Zoomcamp
- software systems → search for MIT 6.824, CMU 15-445

**A2b. context7** — for every framework/library the goal implies, resolve and query docs:
```
mcp__plugin_context7_context7__resolve-library-id  topic="<library name>"
mcp__plugin_context7_context7__query-docs  tokens=4000  topic="<library name> getting started overview"
```
For broad goals (e.g. "AI engineering"), hit the top 3–5 implied libraries.

**A2c. Vault graph** — run learningpath.py to find existing notes that already cover sub-topics:
```
python {{SCRIPTS}}/learningpath.py "<goal>" --top 15
```
Notes returned here become `[[wikilinks]]` in the plan instead of duplicated generated content.

Synthesize: merge topics from A2a + A2b, deduplicate, order by prerequisite dependency. Flag any conflicts between sources explicitly.

### A3. Generate concept tree

Before writing files, construct an exhaustive bulleted concept tree (all topics the goal requires, grouped by phase). Verify coverage by cross-checking against:
- The roadmap search results (A2a)
- The library docs overviews (A2b)
- Any authoritative syllabus found

This tree becomes the "no concepts missed" guarantee and seeds both `plan.md` and the day-by-day schedule.

### A4. Write plan files

**Slug:** goal lowercased, spaces → hyphens, punctuation stripped, max 60 chars.
Example: "learn AI engineering" → `learn-ai-engineering`

**Write plan, progress, and index files:** Read `{{SKILLS}}/curriculum/templates/plan-files.md` for the three file templates (plan.md, progress.md, and index.md). Fill all `<placeholder>` values and write to their target paths (`curricula/<slug>/plan.md`, `curricula/<slug>/progress.md`, `curricula/index.md`).

**Generate `.ics` schedule — REQUIRED `AskUserQuestion` call:**

After writing the plan files, call `AskUserQuestion` (as a separate call, not inline) with this question before A5:

> "Generate a calendar .ics file for daily reminders? (one event per day at 08:00 IST, Obsidian deep-link in each event)"
> Options: `Yes, generate it` / `Skip for now`

If **Yes**: generate `curricula/<slug>/schedule.ics` by reading `{{SKILLS}}/curriculum/templates/ics-generator.py`, substituting the four variables (slug, start date from plan `created:`, topics list verbatim from plan's "Topic (day_label)" column, duration_min from time_budget), writing the filled-in script to a temp file, and running it via Bash. For multi-note days, the Obsidian DESCRIPTION link should point to `concepts-01-<topic-slug>` instead of `concepts`.

If **Skip**: continue to A5. Remind user they can run `/curriculum ics` later to generate it retroactively.

### A5. Check for prerequisite overlaps

After writing the plan, read `curricula/index.md`. For any other curricula listed:
1. Run `learningpath.py "<goal>"` to get tag intersection
2. If any day's tags appear in a completed curriculum's `progress.md`, add to `plan.md` prerequisites section and offer `/curriculum next --skip-known`

### A6. Present and confirm

Show the user:
- Phase map (Mermaid text)
- Day-by-day table (first 7 rows + "... N more days") — include the `day_label` / Topic column so labels are visible before generation
- Capstone description
- Count of vault notes reused (saves X days of generation)

Ask: "Generate day 1 now, or save the plan and stop here?"

---

## FLOW B — Day generation: `/curriculum next` / `/curriculum day <N>`

### B0. Resolve which day

- `next`: read `curricula/index.md` frontmatter `active:` to find slug, read `progress.md` to find lowest day where Concepts = ☐
- `day <N>`: use slug from `active:`, generate day N regardless of progress state
- `--skip-known`: read completed-curriculum `progress.md` files, find days in this curriculum whose concept tags are all ✓ in a prior curriculum, skip them

### B1. Per-day research (targeted)

Derive `<YEAR>` from today's date (available in the session context) before running searches. Do not hardcode a year.

Before generating, run all of the following in parallel:

**B1a. Topic refresh:**
- `WebSearch "<day topic> <goal> tutorial <YEAR>"`
- `WebSearch "<day topic> best practices <YEAR>"`

**B1b. Library version lookup — for every library this day's practical will use:**
- `WebSearch "latest stable <library> version <YEAR> pypi"` — cross-check against PyPI release page
- `mcp__plugin_context7_context7__resolve-library-id` + `mcp__plugin_context7_context7__query-docs` for the resolved library — pull changelog / migration guide so deprecated APIs are avoided
- If a newer major version exists (e.g. library was on v1.x at plan time, v2.x is now stable), **use the new version** and note the upgrade in a `> [!note]` callout at the top of the practical

**B1c. Alternative technology check:**
- `WebSearch "best library for <task> python <YEAR>"` — if a better-maintained or more widely adopted alternative has emerged since the plan was written, flag it to the user and ask whether to swap before generating

Pin every dependency in `day-NN/practical.md` to the **latest stable version confirmed in B1b**, not the version from plan-creation time.

### B2. Write concept note(s) for `day-<NN>/`

Create folder `curricula/<slug>/day-<NN>/` first (shell: `mkdir -p`). Write all day files inside it.

#### B2a. Apply the split heuristic (deterministic)

Derive this day's concept set from the plan's "Key concepts" column for day N:

- **1 concept → 1 note:** write `concepts.md` (original behavior, fully backward-compatible).
- **2–3 concepts → N notes:** write `concepts-01-<topic-slug>.md`, `concepts-02-<topic-slug>.md`, … — one atomic note per distinct concept, each fully self-contained (own declarative title, own diagram, own worked example, own when-not-to-use, own recall prompts). Do **not** also write a `concepts.md`; the numbered notes are the concepts for this day. Use a short kebab-case slug for each topic (e.g. `concepts-01-attention-mechanism.md`).
- **>3 concepts in plan → warn + cap:** add a `> [!warning]` callout at the top of the first generated concept note: "Day <N> has >3 atomic concepts assigned in the plan. Only the first 3 are generated here — run `/curriculum replan` to redistribute the remaining concepts into adjacent days." Generate at most 3 concept notes.
- Set `needs_split: true` on any note that, despite best effort, still covers more than one coherent concept (for a later `/uplift` or `/lint` pass). Otherwise `needs_split: false`.

**Within-day cross-linking for multi-note days:**
- Each `concepts-0K` note's `## See also` links to the adjacent notes within the same day: `concepts-0(K-1)` and `concepts-0(K+1)`.
- `concepts-01` also links back to the previous day's last concept file; the last concept note also links forward to next day's first concept file.
- `practical.md` and `review.md` `prerequisites:` list **all** this day's concept files (e.g. `["[[curricula/<slug>/day-<NN>/concepts-01-<slug>]]", "[[curricula/<slug>/day-<NN>/concepts-02-<slug>]]"]`).

#### B2b. Write each concept note

Type: `learning` (Concept). Must pass Universal U1–U7 + Concept add-ons per Quality Rubric v3 (checks L1–L14). Apply the template once per concept note (filename is `concepts.md` for single-concept days, `concepts-0N-<topic-slug>.md` for multi-concept days).

> **Depth vs. atomicity:** The enriched template adds depth **within** one atomic concept. It does NOT relax U3. If writing any section reveals a second coherent idea, stop — split per B2a first, then complete both notes separately.

**Read** `{{SKILLS}}/curriculum/templates/concept-note.md` and fill every section for this concept. The template includes 14 required concept-note sections (L1–L14), including the four mastery-depth sections:
- `## Why this exists (motivation)` — the problem it was invented to solve and what came before
- `## Cost & complexity` — time/space/compute cost with real figures (or practical overhead for non-quantitative concepts)
- `## Edge cases & boundary conditions` — where the concept itself breaks down (distinct from runtime errors in practical)
- `## Variations & extensions` — named variants and frontier extensions, one line each

At least one of the 4–5 Recall prompts must be drawn from these depth sections (cost bound, a specific edge case, or a named variant and its trade-off).

### B3. Write `day-<NN>/practical.md`

Type: `cookbook` (Procedure). Must pass Universal U1–U7 + Cookbook add-ons per Quality Rubric v3 (checks C1–C6).

**Read** `{{SKILLS}}/curriculum/templates/practical.md` and fill every section. Write to `curricula/<slug>/day-<NN>/practical.md`.

### B4. Write `day-<NN>/review.md`

Type: `reference` (lookup/quiz). Must pass Universal U1–U7 + Reference add-ons per Quality Rubric v3 (checks R1–R3).

**Read** `{{SKILLS}}/curriculum/templates/review.md` and fill every section. Write to `curricula/<slug>/day-<NN>/review.md`.

---

### B5. Quality self-check

Before updating progress, score each generated file against **Quality Rubric v3** (defined in `CLAUDE.md`). This mirrors what `/lint` would flag — run it here so the day is correct from the start.

**Read** `{{SKILLS}}/curriculum/templates/quality-rubric.md` for the full check tables (U1–U7 + L1–L14 for concepts, C1–C6 for practical, R1–R3 for review). Score each file in turn, printing a PASS / FAIL line per criterion. For any FAIL, regenerate the missing/failing section inline before proceeding to B6. If all PASS, print `✓ Day <N> quality check passed` and continue to B6.

---

### B6. Update progress and log

**Update `curricula/<slug>/progress.md`:**
- Tick Concepts = ✓, fill Title cell with `day_label`, mark Practical and Review as ☐ (user completes those)
- Update `active_day` frontmatter to N

**Append to `wiki/log.md`:**
```
## [YYYY-MM-DD] curriculum | <slug> day <N>
- Topic: <day_label>
- Files: day-<NN>/concepts*.md (<N> concept note(s)) · day-<NN>/practical.md · day-<NN>/review.md
- Research: <sources used>
```

---

## FLOW C — `/curriculum list`

Read `curricula/index.md`, then for each curriculum read its `progress.md` to get current `active_day`. Output:

```
## Your Curricula

| Curriculum | Goal | Status | Progress | Started |
|------------|------|--------|----------|---------|
| learn-ai-engineering | Learn AI Engineering | active | 5/60 days | 2026-05-20 |
| pandas-joins | Learn pandas joins | completed | 5/5 days | 2026-05-10 |
```

Mark active curriculum with ★.

---

## FLOW D — `/curriculum audit <slug>`

1. Read `curricula/<slug>/plan.md` — extract every concept from the concept tree (all bullet points not marked with `[[link]]`)
2. Glob `curricula/<slug>/day-*/concepts*.md` — extract H2 section headings from each file (covers both single-note `concepts.md` and multi-note `concepts-01-*.md` … `concepts-0N-*.md`)
3. Diff: concepts promised in plan vs concepts found in generated files
4. Output a coverage report:

```
## Coverage audit: <slug>

✓ 34 concepts covered
⚠ 8 concepts not yet generated (days 12–15 not created yet)
✗ 2 concepts missing from generated days:
  - "attention masks" — promised in day 7 but not found in any day-07/concepts*.md
  - "gradient checkpointing" — promised in day 11 but not found in any day-11/concepts*.md
```

Offer to regenerate the flagged days.

---

## FLOW E — `/curriculum replan`

Called when user has marked days as "too easy / too hard / skipped" in `progress.md` reflections.

1. Read `progress.md` — find days with skip/hard/easy markers
2. Re-run A2 research with context: `"<goal> <topic> for <starting_level + delta> learner"`
3. Rewrite `plan.md` from `active_day + 1` forward, preserving completed days
4. Archive old plan: `mv curricula/<slug>/plan.md curricula/<slug>/plan.v<N>.md`
5. Write new `plan.md`
6. Report: "Replanned days X–N. Old plan archived to plan.v1.md."

---

## FLOW F — `/curriculum grade <N>`

### F1. Resolve slug and pad day

Read `curricula/index.md` frontmatter `active:` for slug. Pad N: `nn = str(N).zfill(2)`.

### F2. Check for hand-written grader

If `curricula/<slug>/day-<nn>/grader.py` exists → go to F4 (run it directly).

### F3. Auto-generate grader from Required outputs table

Read `curricula/<slug>/day-<nn>/practical.md`. Parse the `## Required outputs` table — extract every row's file path and key requirements column.

**Read** `{{SKILLS}}/curriculum/templates/grader-template.py`. Adapt the per-output blocks exactly to the rows in the `## Required outputs` table:
- `.csv` → pandas shape + column presence + null checks
- `.json` → key presence + type checks
- `.pkl` → `pickle.load()` succeeds (no exception)
- `.pt` → `torch.load()` succeeds
- `.png` → existence check only

Write the adapted script to `curricula/<slug>/day-<nn>/grader.py` via Bash (never Write tool for Python files).

### F4. Run grader

```
python curricula/<slug>/day-<nn>/grader.py
```

Capture stdout + exit code.

### F5. Append result to review file

Append to `curricula/<slug>/day-<nn>/review.md`:

```markdown
## Grade result (auto)
- Ran: <YYYY-MM-DD>
- Result: PASS / FAIL
- Checks: <N> passed, <M> failed
- Details:
  <grader stdout, indented>
```

### F6. Update progress.md

In the `| <N> | ... | Grade |` column of `progress.md`, set the Grade cell to `PASS` or `FAIL`.

---

## FLOW G — `/curriculum export <slug>`

Generate `curricula/<slug>/SHARE.md` containing:
- Full `plan.md` content
- Concept tree (text only, no wikilinks to local vault)
- Dataset list + versions
- Practical objectives (not full code — just the "By the end..." line per day)
- `manifest.json` in the same folder: `{ "curriculum_id": "<uuid>", "goal": "...", "days": N, "datasets": [...], "tools": [...] }`

No personal `progress.md` content is included.

---

## FLOW H — `/curriculum import <path>`

1. Read `<path>/SHARE.md` or `<path>` if it's a single file export
2. Extract goal, days, datasets, tools
3. Create `curricula/<new-slug>/plan.md` from the import content
4. Write fresh `progress.md` (all days ☐)
5. Add to `curricula/index.md`
6. Confirm: "Imported '<goal>' as <new-slug>. Run `/curriculum next` to start generating days."

---

## FLOW I — `/curriculum today`

1. Read `curricula/index.md` active slug
2. Read `curricula/<slug>/plan.md` frontmatter `created:` + time_budget days
3. Compute target day = `(today - created).days + 1`
4. Check `progress.md` — is this day generated?
   - If yes: "Today is day N: <topic>. Files ready: [[day-NN/concepts]] (or [[day-NN/concepts-01-<slug>]] … for multi-note days) · [[day-NN/practical]] · [[day-NN/review]]"
   - If no: "Today is day N: <topic>. Generating now..." → run Flow B for day N

---

## FLOW J — `/curriculum resume <slug>`

Update `curricula/index.md` frontmatter `active:` to `<slug>`. Confirm: "Active curriculum set to <slug>. Run `/curriculum next` to continue from day N."

---

## FLOW K — `/curriculum ics [<slug>]`

Generate or regenerate `schedule.ics` for any curriculum (retroactive fix if skipped during setup).

1. Resolve slug: if `<slug>` provided, use it; else read `curricula/index.md` frontmatter `active:`
2. Read `curricula/<slug>/plan.md` — extract `created:` date, `time_budget:` (parse minutes), and the **Topic (day_label)** column from the day-by-day table (one `day_label` per row)
3. Read `{{SKILLS}}/curriculum/templates/ics-generator.py`, substitute the variables (slug, start date, topics list, duration_min, vault path), write the filled-in script to a temp file, and run via Bash
4. Confirm: "Written N events to `curricula/<slug>/schedule.ics`. Import into Google Calendar / Outlook / Apple Calendar."

---

## FLOW L — `/curriculum done <N>`

Quiz the user on day N's recall prompts via self-assessment, then archive the three day files to `done/` on pass.

### L1. Resolve slug and day

- Read `curricula/index.md` frontmatter `active:` for slug (or infer from context)
- Pad N to two digits: `nn = str(N).zfill(2)`
- Confirm folder exists: `curricula/<slug>/day-<nn>/` with `concepts.md`, `practical.md`, `review.md` inside

### L2. Extract recall prompts

Read `curricula/<slug>/day-<nn>/review.md`. Extract every `> [!question]` block — the text on the same line after `> [!question]`. Collect up to 5 questions. Also collect the matching `> [!answer]-` lines for scoring reference (shown after user self-rates).

### L3. Quiz via AskUserQuestion

Call `AskUserQuestion` with a single question. Format the question field to show all recall questions numbered:

```
Day N recall quiz — answer each in your head, THEN self-rate below.

1. <question 1 text>

2. <question 2 text>

3. <question 3 text>

(answers will be revealed after you choose)
```

Options:
- **"Nailed it — archive day N"** — got all or nearly all right; move files to done/
- **"Got most — archive anyway"** — got 2/3+ right; archive with a note
- **"Need more review"** — not confident yet; leave files in place

### L4. Reveal answers

After the user selects, print the answers from the `> [!answer]-` blocks so they can verify their self-assessment:

```
Answers:
1. <answer 1>
2. <answer 2>
3. <answer 3>
```

### L5. Archive (if "Nailed it" or "Got most")

1. Create `curricula/<slug>/done/` directory if it doesn't exist — use shell: `mkdir -p curricula/<slug>/done`
2. Move the entire day folder via shell (never Write tool):
   On Windows use PowerShell: `Move-Item curricula/<slug>/day-<nn> curricula/<slug>/done/day-<nn>`
3. Tick all three checkboxes in `curricula/<slug>/progress.md` for day N:
   - Change `| N | <day_label> | ☐ | ☐ | ☐ |` → `| N | <day_label> | ✓ | ✓ | ✓ |`
   - If "Got most" add a note in the Notes column: `partial`
4. Recompute done-day count and update `curricula/index.md`:
   - Read `curricula/<slug>/progress.md` and count rows where all three checkboxes are ✓
   - In `curricula/index.md`, find the row for `<slug>` and update the `Progress` cell (e.g. `3/75 days`)
5. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] curriculum | <slug> day N done
   - Archived: day-<nn>/ → done/day-<nn>/
   - Quiz result: <nailed it | got most>
   ```
6. Confirm: "Day N archived to `curricula/<slug>/done/day-<nn>/`. Progress updated (Concepts ✓ Practical ✓ Review ✓). Index: <new count>/<total> days."

### L6. Skip archive (if "Need more review")

- Do NOT move any files or tick any checkboxes
- Report: "Day N not archived. Revisit `[[curricula/<slug>/day-<nn>/review]]` and run `/curriculum done N` again when ready."

---

## Behavior rules (always apply)

1. **Anonymization** — never mention employer name in any generated file; use "our platform" / "our workload"
2. **Day folders** — each day lives in its own `<slug>/day-<NN>/` folder containing `concepts*.md` (1–3 atomic concept notes per day — see B2a), `practical.md`, `review.md`, `grader.py`, and `outputs/`; never flat files at the slug root
3. **Examples are concrete** — real numbers, real library names, real dataset rows; never `<placeholder>` or `<your_value>`
4. **Version-pin all code with latest stable versions** — every code block starts with `# tested: lib==version`; versions must be the latest stable release confirmed via B1b at day-generation time, not whatever was current at plan-creation time; never copy version pins from a prior day without re-checking
5. **Quality Rubric v3** — apply U1–U7 universally + type-specific add-ons per note `type:`; verified by the B5 quality self-check (read `templates/quality-rubric.md`) before marking any day done:
   - `day-NN/concepts*.md` (**each** atomic concept note) → type `learning`: U1–U7 + L1–L14:
     - L1 Intuition (mental model), L2 Formal definition, L3 2+ Worked examples with real code + real output, L4 Why does this work?, L5 Mermaid diagram (use `<br/>` not `\n`), L6 Common misconceptions table, L7 Trade-offs vs alternatives table, L8 Sources ≥2 dated citations, L9 day_label verbatim in frontmatter, L10 confidence:high + level: set
     - **L11 Why this exists (motivation)** — problem it was invented to solve; names predecessor + limitation
     - **L12 Cost & complexity** — time/space/compute cost with real figures; O-notation where applicable
     - **L13 Edge cases & boundary conditions** — where the concept itself breaks down; distinct from runtime errors
     - **L14 Variations & extensions** — named variants and frontier extensions, one line each
   - `day-NN/practical.md` → type `cookbook`: U1–U7 + version-pinned code (C1) + what-can-go-wrong table (C2) + prerequisite wikilink (C3) + Required outputs table with `day-<NN>-` filenames (C4) + checkpoint code (C5) + day_label verbatim (C6)
   - `day-NN/review.md` → type `reference`: U1–U7 + self-check questions table 5–10 rows (R1) + see-also links to concepts/practical/next-day (R2) + day_label in frontmatter and H1 (R3)
   - All files get `maturity: seedling` on creation; user promotes to `budding`/`evergreen` as they revise
   - **Depth means depth WITHIN one atomic concept** — the enriched template does NOT relax U3 (one idea per note). If writing any section reveals a second coherent idea, split per B2a first.
6. **Recall prompts are mandatory** (U4) — concept notes get 4–5 `> [!question]` / `> [!answer]-` pairs; **at least one must be drawn from L11–L14** (cost bound, edge case, or named variant); practical and review get 2+ pairs; this is the highest-evidence retention intervention
7. **Declarative titles** (U1) — concept note H1 states a claim ("Transformers use self-attention to relate tokens at any distance"), not a noun ("Attention Mechanism"); practical and review H1s may use the `day_label` phrase
8. **Re-research per day** — do not reuse stale day-1 research; run targeted search before each day generation
9. **Shell for file ops** — any copy/move uses Bash `cp`/`mv` or PowerShell `Move-Item`, never Write tool
10. **Log every action** to `wiki/log.md`
11. **Output filename consistency** — every output file name starts with `day-<NN>-` (e.g. `day-07-results.csv`). The `## Required outputs` table is the single source of truth — the save block, checkpoint, and grader (Flow F3) must reference the exact same filenames. Never generate a table entry and a code block that disagree.
12. **Index always reflects done count** — Flow L5 (`/curriculum done`) must update `curricula/index.md` Progress column after archiving. Never leave the index showing a stale `0/N`.
13. **Mermaid line breaks** — inside node labels always use `<br/>`, never `\n`. `\n` is a literal backslash-n in Mermaid and will not render as a line break.
14. **Canonical `day_label`** — every day has a canonical short label (≤6 words) set in `plan.md`'s Topic column; reuse it verbatim in `progress.md` Title column, every note's `day_label:` frontmatter, and the `.ics` SUMMARY. Never reword it between files. The concept note H1 is a separate declarative claim derived from (but not identical to) the label.
15. **Confidence is always `high`** — all curriculum notes default to `confidence: high`; do more research rather than lowering confidence. Never write `confidence: medium` or lower for generated curriculum files.
16. **`level:` frontmatter on concept notes** — set `level: easy|moderate|advanced` on every `concepts*.md`; values interleaved across the curriculum (no difficulty folders), signalling difficulty for spaced-repetition and `/lint` scoring.
