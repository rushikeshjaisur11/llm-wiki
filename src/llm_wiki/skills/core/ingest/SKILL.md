---
name: ingest
description: Add any source to the wiki — URL, file, batch folder, research topic, or study topic. Always ends with the note written, cross-links added, wiki/index.md updated, and wiki/log.md appended. Use for all knowledge ingestion. Replaces /research, /study, /file-intel, and /process-files.
---

# Ingest — Add to Wiki

Vault root: `{{VAULT}}/`

## Vault Tool Detection (run before every ingest)

Before writing any note, detect the user's vault tool by reading the `vault-tool:` line from the vault's CLAUDE.md:

```
Read: {{VAULT}}/CLAUDE.md
Look for line: vault-tool: <value>
```

The value will be one of: `obsidian`, `foam`, `logseq`, `markdown`.

Apply the formatting rules for that tool throughout the note. If the line is missing or unreadable, default to `markdown` (safest fallback).

---

## Note Quality Standards

Every note must score 7/7 on the Quality Rubric v2 (canonical in `CLAUDE.md` § Note-Writing Checklist). Apply these rendering rules based on vault tool:

| Feature | Obsidian | Foam | Logseq | Plain MD |
|---|---|---|---|---|
| Mermaid | ✅ native | ✅ (extension) | ✅ native | ❌ use ASCII table |
| Callouts `> [!x]` | ✅ native | ❌ use bold blockquote | ❌ use bold blockquote | ❌ use bold blockquote |
| Wikilinks `[[...]]` | ✅ native | ✅ (Foam ext) | ✅ native | ❌ use relative links |

**Mermaid type selection:** pipeline/flow → `flowchart LR` · decision → `flowchart TD` · protocol/message → `sequenceDiagram` · benchmarks → `xychart-beta`

**Node colors:** `fill:#27ae60` green=recommended · `fill:#e74c3c` red=error · `fill:#f39c12` orange=warning · `fill:#3498db` blue=info

**Callouts (Obsidian):** `> [!tldr]` summary · `> [!example]` worked example · `> [!tip]` best practice · `> [!warning]` pitfall

**Examples must be concrete:** real numbers (GB/TB, ms, row counts), real function names, no `<placeholder>` or `TODO`.

**Separators:** `---` between every H2. **Wikilinks:** `[[folder/slug]]` format.

---

## Mode detection

Detect from the argument passed:

| Argument | Mode |
|----------|------|
| YouTube URL (`youtube.com/watch`, `youtu.be/`, `youtube.com/shorts/`) | YouTube |
| `https://` or `http://` URL (non-YouTube) | URL |
| File path with extension (.pdf, .md, .docx, etc.) | Single file |
| Image file path (.png, .jpg, .jpeg, .gif, .svg, .webp) | Single file (image) |
| Directory path (ends in `/` or is a folder) | Batch folder |
| `research: <topic>` | Research |
| `study: <topic>` | Study |
| Topic name only | Ask: "Research (web search) or Study (scaffold from vault)?" |
| No argument | Ask: "What are you adding? (URL, file, folder, or topic)" |

---

## YouTube mode

1. Run: `defuddle parse <url> --md`
   This returns the full transcript with timestamps + page metadata (title, channel, description).

2. Parse the defuddle output to extract:
   - **Title** — from the page `<title>` or first H1
   - **Channel / Speaker** — from the channel name in the metadata
   - **Duration** — from metadata if available
   - **Publish date** — from metadata if available
   - **Chapters** — if the description contains a timestamp list (`HH:MM` or `MM:SS` pattern), treat those as chapter markers. Otherwise skip.
   - **Full transcript** — the main body from defuddle output

3. Classify to vault folder:
   - `research/`         — conference talks, paper walkthroughs, architecture deep-dives, LLM research
   - `learning/`         — tutorials, course lectures, how-to walkthroughs, tool demos
   - `data-engineering/` — pipeline demos, GCP/Spark/Kafka walkthroughs, production war stories

   If unclear, ask: "Which folder? (research / learning / data-engineering)"

4. Synthesize the transcript. Extract:

   **Thesis** — 1–2 sentences: what is the speaker trying to convince you of? What problem do they claim to solve?

   **Key Insights** (5–8 bullets) — the most important ideas, not paraphrases. Concrete and specific. Must include real numbers, benchmark results, or code-level details where the speaker provides them.
   Example: "Paged attention reduces KV cache fragmentation by allocating in fixed-size blocks, enabling ~3× longer context at same memory budget."

   **Key Moments** (3–8 timestamp anchors) — moments where a major concept is introduced, a demo begins, a key claim is made, or a chapter starts. Use the nearest timestamp from the transcript. Format: `[MM:SS]` or `[HH:MM:SS]`.

   **Quotable moments** — 1–3 direct quotes worth preserving verbatim. Short (1–2 sentences each).

   **Technical terms introduced** — new tools, frameworks, or concepts named in the video that may warrant their own vault pages. Check `wiki/index.md`; flag any not present with "(→ /ingest?)".

5. Ask: "Does this capture what matters? Anything to adjust?"
   Adjust based on response.

6. Write `<folder>/<slug>.md` (slug = title lowercased, spaces → hyphens, strip punctuation) following **Note Quality Standards** above:

   ```markdown
   ---
   title: <Title>
   created: <TODAY>
   updated: <TODAY>
   last_verified: <TODAY>
   confidence: medium
   provenance: extracted
   tags: [<topic-tags>, video]
   type: <research | learning | data-engineering>
   source: "<youtube_url>"
   source-type: video
   channel: "<Channel Name>"
   published: "<YYYY-MM-DD if known>"
   duration: "<HH:MM:SS if known>"
   related: []
   ---

   # <Title>

   > **Up:** [[<folder>/index]]

   > **Channel:** <Channel> | **Published:** <date> | **Duration:** <duration>
   > **Watch:** <youtube_url>

   ## Thesis
   <!-- 1–2 sentence summary of the speaker's main argument — include the key claim with a number if one exists -->

   ---

   ## Key Insights
   <!-- 5–8 bullets — concrete and specific, real numbers, not paraphrases -->
   - ...

   ---

   ## How It Works
   <!-- If the video explains a system, process, or architecture — add a Mermaid diagram.
        Skip this section if the video is purely opinion/interview with no technical mechanism. -->

   ```mermaid
   flowchart LR
       A[Component] --> B[Component] --> C[Output]
   ```

   > [!example] Worked example from the video
   > <!-- Pull a concrete example the speaker gave — real numbers, real benchmark, real code -->

   ---

   ## Key Moments
   | Time | What happens |
   |------|-------------|
   | [MM:SS] | ... |

   ---

   ## Quotable
   > "..."

   ---

   ## Chapters
   <!-- Only if the video has explicit chapters — list with timestamps and 1-line summary each -->

   ---

   ## Technical Terms
   <!-- Link to existing vault pages; flag new ones with "(→ /ingest?)" -->

   ## Open Questions
   <!-- What this raised that I want to dig into — be specific -->
   ```

7. Do NOT include the full transcript in the note.
   Exception: if the user explicitly says "keep the transcript", append it under a collapsed block:
   ```html
   <details>
   <summary>Full transcript</summary>

   <!-- paste transcript here -->

   </details>
   ```

8. → **[Wiki Update]**

---

## URL mode

1. Use the `defuddle` skill to fetch and clean the URL into markdown
2. Write a 2–3 sentence synthesis of key insights → ask: "Does this capture what matters?"
3. Adjust based on response, then classify to vault folder:
   - `research/` — deep technical: papers, architecture, LLMs, agents, systems
   - `learning/` — guides, tutorials, how-tos, courses
   - `data-engineering/` — pipelines, GCP tools, schemas, Kafka, Airflow
4. Write `<folder>/<slug>.md` (slug = title lowercased, spaces → hyphens) following the **Note Quality Standards** above:
   - Open with `## TL;DR` — 1–2 punchy sentences
   - Add `---` separators between H2 sections
   - For any process, architecture, or flow described → add a Mermaid diagram
   - For any comparison of options/tools → add a table with a "When to Use" column
   - For any key concept → add a `> [!example]` callout with concrete numbers
   - For warnings or gotchas → use `> [!warning]` or `> [!tip]` callouts
5. **Image handling**: After defuddle returns markdown, scan the content for `![alt](http...)` remote image references (supported extensions: `.png .jpg .jpeg .gif .svg .webp`):
   - For each remote image URL, derive a local filename: `<note-slug>-<n>.<ext>` (n = 1, 2, …)
   - Ensure `{{VAULT}}/attachments/` exists (create with Bash `mkdir -p` if not)
   - Download: `curl -L --max-filesize 5242880 -o "{{VAULT}}/attachments/<filename>" "<url>"`
   - If download succeeds: replace the `![alt](url)` reference in the note with `![[attachments/<filename>]]`
   - If download fails or file > 5 MB: leave the original remote URL embed in place unchanged
   - Only process extensions in the supported list; skip `.gif` if it exceeds 2 MB
6. → **[Wiki Update]**

---

## Single file mode

**If the source file is an image** (extension `.png .jpg .jpeg .gif .svg .webp`):
1. Read the image visually
2. Ask: "What is this diagram/image about? (One line caption)" — use this as the note title
3. Classify to vault folder (same rules as URL mode)
4. Copy the image to `attachments/`: run `cp "<source>" "{{VAULT}}/attachments/<slug>.<ext>"` via Bash
5. Write `<folder>/<slug>.md`:
   ```markdown
   ---
   title: <Caption>
   created: <TODAY>
   updated: <TODAY>
   last_verified: <TODAY>
   confidence: medium
   provenance: extracted
   tags: [<topic-tags>, diagram]
   type: <research | learning | data-engineering>
   source: "<original filename>"
   related: []
   ---

   # <Caption>

   > **Up:** [[<folder>/index]]

   ![[attachments/<slug>.<ext>]]

   ## Description
   <!-- 2–3 sentences describing what the diagram shows -->

   ## Related Notes
   <!-- [[wikilinks to related vault notes]] -->
   ```
6. → **[Wiki Update]**

**If the source file is a document** (PDF, PPTX, XLSX, DOCX, CSV, JSON, MD, TXT):
1. Read the file completely
   - PDFs: read in 10-page chunks (`pages: "1-10"`, `"11-20"`, etc.) until all pages are read
   - Other formats: read in one call
2. Write 2–3 sentence synthesis → ask user to confirm emphasis
3. Classify to vault folder (same rules as URL mode)
4. Write full markdown note following **Note Quality Standards** above:
   - `## TL;DR` at the top — 1–2 sentences: what it is, the key takeaway
   - `---` separators between H2 sections
   - At least one Mermaid diagram if the source contains any process, architecture, or data flow
   - `> [!example]` callout for any key concept explained abstractly — ground it with real numbers
   - `> [!warning]` or `> [!tip]` for any critical pitfalls or best practices called out in the source
   - Comparison tables (with a "When to Use" or "Tradeoff" column) wherever alternatives are compared
5. → **[Wiki Update]**

---

## Batch folder mode

1. `Glob` all supported files in the folder: PDF, PPTX, XLSX, DOCX, CSV, JSON, MD, TXT, PNG, JPG, JPEG, GIF, SVG, WEBP
   Show image files separately from document files in the file list.
2. Show the file list and ask:

   > Found **N files**. How should I process them?
   > - **Sequential** — I read and write everything myself (slower, but reliable — subagents can't always write to the vault)
   > - **Subagents** — one parallel agent per file (faster for large batches, but agents may hit Write permission denials)

   Wait for the user's answer before continuing.

3a. **If Sequential**: process each file one at a time — read it fully, write source note, write summary note, then move to the next.

3b. **If Subagents**: Send a **single message** with one `Agent` tool call per file (all in parallel):

   Subagent prompt template (fill in placeholders):
   ```
   Process a single file for an Obsidian vault.
   File: <ABSOLUTE_PATH> | Date: <TODAY> | Vault root: {{VAULT}}/

   Step 1: Read the COMPLETE file.
   - PDFs: check total page count, read in 10-page chunks until all pages done.
   - Images (.png, .jpg, .jpeg, .gif, .svg, .webp): read visually, ask the user for a one-line caption, then treat as an image ingest (see image branch in single file mode). Copy to attachments/, write a note with ![[attachments/<slug>.<ext>]] embed. Return RESULT: SUCCESS with the slug.
   - Other formats: read in one call.
   - If truly unreadable/binary (not an image): return RESULT: SKIPPED | FILE: <name> | REASON: unreadable

   Step 2: Classify into one vault folder:
   - research/     — papers, deep dives, LLMs, agentic systems
   - learning/     — tutorials, guides, courses, how-tos
   - data-engineering/ — pipelines, GCP, schemas, Kafka, SQL
   - personal/     — goals, health, reflections, admin
   - archive/      — completed or doesn't fit elsewhere

   Step 3: Write full markdown source to: {{VAULT}}/<folder>/sources/<stem>.md
   The <stem> is filename without extension, spaces → underscores.
   Content must be COMPLETE — every word from original, verbatim. Not a summary.
   Use frontmatter: title, created, updated, last_verified, confidence, provenance, tags, source (original filename), type, related.

   Step 4: Write summary note to: {{VAULT}}/<folder>/<stem>.md
   Format:
   - frontmatter (title, created, updated, last_verified, confidence, provenance, tags, type, source, related)
   - ## TL;DR — 1–2 punchy sentences: what it is, why it matters, the key insight
   - ## Key Points — 5–8 bullets, concrete and specific (real numbers, real names, not vague summaries)
   - ## How It Works — include at least one Mermaid diagram (flowchart or sequenceDiagram) if the source explains a process, architecture, or flow
   - ## Key Example — a `> [!example]` callout with a concrete worked example (real inputs → real outputs with numbers)
   - ## Trade-offs or When to Use — comparison table if alternatives are discussed
   - ## Related — leave placeholder comment

   Step 5: Return exactly:
   RESULT: SUCCESS
   FILE: <original filename>
   FOLDER: <vault-folder>
   STEM: <stem>
   TOPICS: <3-6 comma-separated topic keywords>
   ```

4. Collect results. Cross-link notes that share topic keywords (add wikilinks under `## Related`).
5. Ask: "Delete original files from the folder?" → if yes, `rm` each successfully processed source file.
6. → **[Wiki Update — batch]**

---

## Inbox drops (image detection)

When the user runs `/ingest` with no argument, or when an `inbox/` scan is performed as part of lint, check for image files in `{{VAULT}}/inbox/`:

1. `Glob inbox/*.{png,jpg,jpeg,gif,svg,webp}` (case-insensitive) — list any found images.
2. If images are found, display them separately from documents:

   > Found **N image(s)** in inbox:
   > - `inbox/screenshot-2026-04-20.png`
   > - `inbox/diagram.jpg`
   > For each, I'll ask: **"What folder does this belong in, and what's the one-line caption?"**

3. For each image, ask: "What is this? (e.g. `research — Kafka consumer group architecture`)"
   Accept: `<folder> — <caption>` or free text; infer folder if obvious from caption.
4. Process using the **Single file mode (image branch)** above:
   - `cp` to `attachments/<slug>.<ext>`, write `<folder>/<slug>.md` with embed + description
5. After writing the note, `rm` the original from `inbox/` (with user confirmation if processing > 1 image at once).
6. → **[Wiki Update]** for each written note.

---

## Research mode

1. **Search existing notes** (zero token cost):
   ```
   python {{SCRIPTS}}/search.py "<topic>" --top 5
   ```
   Read the returned note files. Note what's already known (definitions, gaps, existing coverage).
   If `NO_RESULTS`: fall back to reading `wiki/index.md` for keyword matching.
2. `WebSearch` — at least 3 sources, prefer 2024–2026
3. Show 2–3 sentence synthesis → ask: "Anything to emphasize or cut?"
4. Write `research/<slug>.md`:

   ```markdown
   ---
   title: <Topic>
   created: <TODAY>
   updated: <TODAY>
   last_verified: <TODAY>
   confidence: medium
   provenance: inferred
   tags: [<topic-tags>]
   type: research
   source: <primary source URL or "web-search">
   source-count: <N sources used>
   related: []
   ---

   # <Topic>

   > **Up:** [[research/index]]

   ## TL;DR
   <!-- 1–2 punchy sentences: what this is, why it matters, the key insight -->

   ---

   ## Summary
   <!-- 3–5 sentence overview — include at least one concrete number or benchmark -->

   ---

   ## How It Works
   <!-- Architecture, mechanism, or process.
        Obsidian/Logseq/Foam: use a Mermaid diagram (flowchart LR for pipelines,
        sequenceDiagram for message flows, flowchart TD for decisions).
        Plain Markdown: use an ASCII flow or structured table instead. -->

   <!-- Obsidian/Logseq/Foam: -->
   ```mermaid
   flowchart LR
       A[Input] --> B[Process] --> C[Output]
   ```

   <!-- Plain Markdown fallback:
   Input → [Process] → Output
   -->

   <!-- Follow with a concrete worked example using the correct callout for the vault tool:
        Obsidian:              > [!example] Worked example
        Foam/Logseq/Markdown:  > **Example:** ... -->

   > [!example] Worked example
   > <!-- Real numbers: e.g. "100 GB input → 3 stages → 7.5 GB read with DPP enabled" -->

   ---

   ## Key Concepts
   <!-- Core ideas and definitions — one subsection (###) per concept.
        Each concept: definition + a concrete example or analogy + a comparison table if alternatives exist. -->

   ---

   ## Use Cases
   <!-- Where this is applied — use a table: Use Case | Why This Fits | Alternative -->

   ---

   ## Trade-offs
   <!-- MUST be a comparison table (all tools) or Mermaid decision tree (Obsidian/Logseq/Foam only).
        Columns: Approach | Pros | Cons | When to Use -->

   ---

   ## Current State (as of <TODAY>)
   <!-- Latest tools, models, frameworks, benchmarks — include version numbers -->

   ---

   ## Open Questions
   <!-- What I still want to understand -->

   ---

   ## Related Topics
   <!-- [[wikilinks to related vault notes]] -->

   ## Sources
   <!-- Links to papers, articles, docs used -->
   ```

5. → **[Wiki Update]**

---

## Study mode

1. **Search existing notes** (zero token cost):
   ```
   python {{SCRIPTS}}/search.py "<topic>" --top 5
   ```
   Read returned files → extract relevant content into "What I Already Know".
   If `NO_RESULTS`: fall back to reading `wiki/index.md` for keyword matching.
2. Write `learning/<slug>.md`:

   ```markdown
   ---
   title: <Topic>
   created: <TODAY>
   updated: <TODAY>
   last_verified: <TODAY>
   confidence: low
   provenance: inferred
   tags: [<topic-tags>]
   type: learning
   source: derived
   related: []
   ---

   # <Topic>

   > **Up:** [[learning/<topic-folder>/index]]

   ## TL;DR
   <!-- 1–2 punchy sentences: what this is, why it matters, and the key insight to hold onto -->

   ---

   ## What I Already Know
   <!-- Pulled from existing vault notes — concrete facts and code, not vague recollections -->

   ---

   ## How It Works
   <!-- Mechanism, architecture, or process.
        Obsidian/Logseq/Foam: use a Mermaid diagram (flowchart LR, sequenceDiagram, flowchart TD).
        Plain Markdown: use ASCII art or a Step | Input | Output table instead. -->

   <!-- Obsidian/Logseq/Foam: -->
   ```mermaid
   flowchart LR
       A[Input] --> B[Process] --> C[Output]
   ```

   <!-- Plain Markdown fallback:
   Step 1: Input → [Process] → Output
   Step 2: ...
   -->

   <!-- Concrete worked example — use the correct syntax for the vault tool:
        Obsidian:              > [!example] Worked example
        Foam/Logseq/Markdown:  > **Example:** ... -->

   > [!example] Worked example
   > <!-- Show a concrete end-to-end example: real sizes, real latencies, real row counts.
   >      Before/after is ideal: "Without X: 100 GB read. With X: 7.5 GB read." -->

   ---

   ## Key Concepts
   <!-- One ### subsection per concept. Each must have:
        1. A one-sentence definition
        2. A concrete example (numbers or code)
        3. A comparison table or callout if there are gotchas -->

   ---

   ## Code / Examples
   <!-- Runnable code only — real function names, real config keys, real values.
        Show the bad pattern first (commented), then the correct pattern. -->

   ```python
   # Bad: <why this is wrong>
   # example...

   # Good: <why this works>
   # example...
   ```

   ---

   ## Trade-offs & When to Use
   <!-- Comparison table OR Mermaid decision tree flowchart.
        Columns: Option | Pros | Cons | Use When -->

   ---

   ## Questions & Gaps
   <!-- What I still don't understand — be specific, not "learn more about X" -->

   ---

   ## Resources
   <!-- Links, papers, courses -->

   ## Related Notes
   <!-- [[wikilinks to related vault notes]] -->
   ```

3. → **[Wiki Update]**
4. Ask: "Ready — what do you want to fill in first?"

---

## Learning Folder Awareness

When writing a note into `learning/`, read `{{VAULT}}/SCHEMA.md` and `{{VAULT}}/learning/CONVENTIONS.md` before writing.

Apply these rules:

1. **Frontmatter must include the extended LLM Wiki v2 + v3 fields:**
   ```yaml
   last_verified: <TODAY>          # always set to today when creating
   confidence: high | medium | low  # high = verified against source; medium = mostly verified; low = from memory
   provenance: extracted | inferred | ambiguous
   maturity: seedling              # always seedling on first ingest; /uplift promotes to budding/evergreen
   verified_against_version: "<lib>==<version>"   # omit if not a library note
   superseded_by: null
   contradicts: []
   ```

2. **Determine topic class from tags → set TTL:** Read from `SCHEMA.md` § TTL Rules.

3. **Folder triad prompt**: For notes going into a runtime folder (langgraph, langchain, rag, fastapi, vector-db, llm-infra, agents), ask:
   > "Is this content for a concept note, or does it belong in `production.md`, `cookbook.md`, `troubleshooting.md`, or `changelog.md`?"
   If the user says cookbook/production/troubleshooting, append to the appropriate file rather than creating a new concept note.

4. **Contradiction detection**: After writing the note, search for related pages and check if any existing page contradicts a claim in the new note. If a contradiction is found:
   - Add `contradicts: [[existing-note]]` to new note's frontmatter
   - Add `contradicts: [[new-note]]` to the existing note's frontmatter
   - Add a `> [!warning] Contradiction` callout in the new note pointing to the conflict

5. **Anonymization**: Apply the employer anonymization rule from `CLAUDE.md` — replace employer name with "our platform" / "our workload". This applies to ALL modes (URL, file, batch, research, study) — not only learning/ notes.

---

## Pre-Write Quality Check (runs before writing every note)

Before calling Write on any note, verify the draft contains all 7 flat rubric fields (SCHEMA.md Quality Rubric v2) **plus** typed-rubric fields U4 and U7. For each missing field, generate it inline before writing:

0. **Title not declarative (U1 check)?** → Verify `title:` contains `:` OR a verb (uses, enables, defines, is, are, allows, works, handles, implements, compares, controls…). If it is just a noun phrase (e.g., "Kafka Producers", "Speculative Decoding", "LangGraph State & Reducers"), rewrite it as `Topic: Specific Claim or Key Components`. Em-dash `—` and ampersand `&` do NOT satisfy U1. Run this check first — it costs nothing.

1. **tldr-callout missing?** → Read the note body; generate a `> [!tldr]` Obsidian callout (≤3 lines) summarising what the note is, why it matters, and the key insight. Insert immediately after the H1 title.
2. **diagram missing?** → Scan for processes, pipelines, architectures, or decisions in the content. Generate the most appropriate Mermaid block type (flowchart LR for pipelines, sequenceDiagram for protocols, flowchart TD for decisions). Insert in the most relevant section.
3. **worked-example missing?** → Generate a `> [!example]` callout with concrete numbers, real code, and real results. Pull from the source material; never invent placeholder values.
4. **when-not-to-use missing?** → Add a `## When NOT to Use` section with 3–5 bulleted anti-patterns or scope limits derived from the content.
5. **see-also missing?** → Run `python {{SCRIPTS}}/search.py "<note title and tags>" --top 8` and pick the top 3–5 most relevant results as wikilinks. If search unavailable, read `wiki/index.md` and pick manually.
6. **version-pins missing?** (only for `production.md` / `cookbook.md`) → Scan all fenced code blocks; for any missing `# tested:` comment, add `# tested: <detected-library>==<version-from-source-or-ask>` as first line.
7. **retrieval-prompts missing?** (skip for `type: index`, `type: reference`, `type: meta`) →
   - Read the note body; identify the top 2 most retrievable facts: key thresholds/numbers, API decision criteria, failure modes.
   - Generate a `## Recall prompts` section with 2 `[!question]` + `[!answer]-` pairs. Place before `## See Also`.
   - Format:
     ```markdown
     ## Recall prompts

     > [!question] <specific fact or decision from this note>
     > [!answer]- <concrete answer — number, API name, failure mode>

     > [!question] When would you NOT use <X covered in this note>?
     > [!answer]- <specific anti-pattern with concrete triggering condition>
     ```
   - Quality bar: each answer must be a concrete fact, not a restatement. "Use partition pruning when predicates match the partition column exactly" ✓. "Use it when appropriate" ✗.
8. **maturity missing?** → Infer and set `maturity:` in frontmatter:
   - New notes always start as `seedling` (content has not yet been verified by re-reading).
   - Exception: if this is an `/ingest` from an official source URL (provenance: extracted) AND all 7 flat fields + recall prompts are present → set `budding`.
   - Never set `evergreen` on first ingest — that requires TTL-within-date verification via `/refresh`.

Anonymization check: scan the full draft for any employer-name tokens; replace silently with "our platform" or "our workload".

This check is mandatory for all modes. A note that scores <7/7 flat AND is missing U4 or U7 must not be written until the missing fields are generated.

---

## Wiki Update (runs after every mode)

This step is mandatory after all modes.

1. **Search for related pages** (zero token cost):
   ```
   python {{SCRIPTS}}/search.py "<new note tags and title keywords>" --top 8
   ```
   These are the pages to cross-link against.
   If `NO_RESULTS`: fall back to reading `wiki/index.md` for keyword matching.
2. For each related page found:
   - Append wikilink under `## Related` or `## Related Notes` or `## See Also` (create the section if missing)
   - If the new note contradicts something on the page, add a `> [!warning]` callout flagging the discrepancy
3. Add new entry to `wiki/index.md` under the correct section (newest-first within section):
   ```
   - [[folder/slug]] — one-line summary (YYYY-MM-DD)
   ```
4. **Cluster maintenance** (for notes written to `learning/`):
   - Confirm the note has `> **Up:** [[learning/<tech>/index]]` in the body. Add it if missing.
   - Open `learning/<tech>/index.md` and verify the new note appears in the notes list. If missing, add a line:
     ```
     - **[[learning/<tech>/<slug>]]** — <one-line description>
     ```
   - Bump `updated:` in the hub's frontmatter to today.

5. Append to `wiki/log.md`:
   ```
   ## [DATE] ingest | <Title>
   - Note: [[folder/slug]]
   - Updated: [[page1]], [[page2]]
   - Mode: <url | file | batch | research | study>
   - Skills_touched: [ingest]
   ```

6. Update search indexes (all four, in order):
   ```
   python {{SCRIPTS}}/build_graph.py --update <folder/slug.md>
   python {{SCRIPTS}}/build_routing.py --update <folder/slug.md>
   python {{SCRIPTS}}/build_index.py --update <folder/slug.md>
   python {{SCRIPTS}}/build_embeddings.py --update <folder/slug.md>
   ```
   If scripts are not found or `wiki/graph.json` does not exist, run full builds instead:
   ```
   python {{SCRIPTS}}/build_graph.py
   python {{SCRIPTS}}/build_routing.py
   python {{SCRIPTS}}/build_index.py
   python {{SCRIPTS}}/build_embeddings.py
   ```
   For batch mode, always run full builds (not `--update`) after all notes are written.

7. **Suggest related pages** (only if `wiki/embeddings.db` exists):
   ```
   python {{SCRIPTS}}/search.py "<new note title and top 3 tags>" --top 8
   ```
   From the results, exclude the newly written note itself. Compute tag Jaccard overlap between the
   new note's tags and each candidate's tags. Rank by combined score (search rank + tag overlap).
   Take top 5 and populate the `related:` field in the new note's frontmatter:
   ```yaml
   related:
     - "[[candidate1]]"
     - "[[candidate2]]"
     ...
   ```
   Skip this step if the search returns NO_RESULTS or `wiki/embeddings.db` does not exist.
