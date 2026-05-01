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

Every note written by this skill — regardless of mode — must follow these standards. They are non-negotiable. The **implementation** of each standard varies by vault tool (see table below); the **intent** does not.

### Feature Support by Vault Tool

| Feature | Obsidian | VS Code + Foam | Logseq | Plain Markdown |
|---------|----------|---------------|--------|----------------|
| Mermaid diagrams | ✅ Native | ✅ with Markdown Preview Mermaid extension | ✅ Native | ❌ Renders as code block — use ASCII/table instead |
| Callouts `> [!tip]` | ✅ Native | ❌ Renders as plain blockquote | ❌ Renders as plain blockquote | ❌ Renders as plain blockquote |
| Wikilinks `[[...]]` | ✅ Native | ✅ with Foam extension | ✅ Native | ❌ Use relative markdown links |
| `---` separators | ✅ | ✅ | ✅ | ✅ |
| Tables | ✅ | ✅ | ✅ | ✅ |
| Fenced code blocks | ✅ | ✅ | ✅ | ✅ |

### 1. Diagrams — Show Flows Visually

Whenever content involves a process, pipeline, architecture, decision, timeline, or numeric comparison, add a visual. **Never replace a diagram with a prose paragraph.**

**Obsidian / Logseq / Foam:**
Use Mermaid fenced code blocks. Choose the right diagram type:
- Multi-step process or pipeline → ` ```mermaid flowchart LR` or `flowchart TD`
- Decision / "when to use X vs Y" → `flowchart TD` decision tree
- Timeline or trigger cadence → `gantt`
- Message sequence between systems → `sequenceDiagram`
- Numeric distribution (durations, throughput, skew) → `xychart-beta`
- Architecture with components and data flows → `flowchart LR` with subgraphs

Color-code nodes by severity/category:
- `style NodeName fill:#e74c3c,color:#fff` — red = critical / error
- `style NodeName fill:#f39c12,color:#fff` — orange = warning
- `style NodeName fill:#27ae60,color:#fff` — green = good / recommended
- `style NodeName fill:#3498db,color:#fff` — blue = informational

**Plain Markdown (fallback):**
Use ASCII art or a structured table to represent the flow. Example:
```
Source → [Parse] → [Enrich] → Sink
                       ↓
                   [Dead Letter]
```
Or use a table with columns like: Step | Input | Output | Notes.

### 2. Highlighted Insights — Surface What Matters

Use visually distinct blocks to mark the most important content so a reader skimming the note can't miss it.

**Obsidian** — use native callouts:
| Callout | When to use |
|---------|------------|
| `> [!tip]` | Non-obvious best practice or rule of thumb |
| `> [!warning]` | Common pitfall, deprecated behavior, or data-loss risk |
| `> [!note]` | Clarification or constraint that qualifies a statement |
| `> [!example]` | Worked example with real numbers, concrete inputs/outputs |

**Foam / Logseq / Plain Markdown** — use bold-prefixed blockquotes:
```markdown
> **Tip:** Non-obvious best practice text here.

> **Warning:** Common pitfall or data-loss risk here.

> **Example:** Concrete worked example with real numbers here.
```

Every note must have at least one highlighted **Example** block with a concrete worked example (real numbers, real code, real results — never `<placeholder>` or `TODO`).

### 3. Concrete Examples with Numbers

Every abstract concept must be grounded with a concrete example immediately following it. Rules:
- Use realistic numbers: dataset sizes in GB/TB, latency in ms, row counts in millions
- Show before/after: what the problem looks like, what the fix produces
- Code examples must be runnable: real function names, real config keys, real values
- Never use `<placeholder>`, `<your-value>`, or `TODO` in code examples

### 4. Comparison Tables

Whenever two or more options, strategies, or tools are compared, use a markdown table. Always include a "When to Use" or "Tradeoff" column. Decision trees (Mermaid flowchart for Obsidian/Logseq/Foam; ASCII for markdown) are preferred when the choice is conditional.

### 5. Section Separators

Use `---` between every major H2 section regardless of vault tool. Improves readability in all renderers.

### 6. Wikilinks

**Obsidian / Foam / Logseq:** Use `[[folder/slug]]` wikilink format.  
**Plain Markdown:** Use standard relative links: `[Note Title](../folder/slug.md)`.

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
   date: <TODAY>
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
   date: <TODAY>
   tags: [<topic-tags>, diagram]
   type: <research | learning | data-engineering>
   source: "<original filename>"
   related: []
   ---

   # <Caption>

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
   Use frontmatter: title, date, tags, source (original filename), type.

   Step 4: Write summary note to: {{VAULT}}/<folder>/<stem>.md
   Format:
   - frontmatter (title, date, tags, type, source, related)
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
   date: <TODAY>
   tags: [<topic-tags>]
   type: research
   source-count: <N sources used>
   related: []
   ---

   # <Topic>

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
   date: <TODAY>
   tags: [<topic-tags>]
   type: learning
   status: in-progress
   related: []
   ---

   # <Topic>

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
4. Append to `wiki/log.md`:
   ```
   ## [DATE] ingest | <Title>
   - Note: [[folder/slug]]
   - Updated: [[page1]], [[page2]]
   - Mode: <url | file | batch | research | study>
   ```

5. Update search indexes (all four, in order):
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

6. **Suggest related pages** (only if `wiki/embeddings.db` exists):
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
