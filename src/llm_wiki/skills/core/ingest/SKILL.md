---
name: ingest
description: Add any source to the wiki — URL, file, batch folder, research topic, or study topic. Always ends with the note written, cross-links added, wiki/index.md updated, and wiki/log.md appended. Use for all knowledge ingestion. Replaces /research, /study, /file-intel, and /process-files.
---

# Ingest — Add to Wiki

Vault root: `{{VAULT}}/`

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

   **Key Insights** (5–8 bullets) — the most important ideas, not paraphrases. Concrete and specific.
   Example: "Paged attention reduces KV cache fragmentation by allocating in fixed-size blocks, enabling ~3x longer context at same memory."

   **Key Moments** (3–8 timestamp anchors) — moments where a major concept is introduced, a demo begins, a key claim is made, or a chapter starts. Use the nearest timestamp from the transcript. Format: `[MM:SS]` or `[HH:MM:SS]`.

   **Quotable moments** — 1–3 direct quotes worth preserving verbatim. Short (1–2 sentences each).

   **Technical terms introduced** — new tools, frameworks, or concepts named in the video that may warrant their own vault pages. Check `wiki/index.md`; flag any not present with "(→ /ingest?)".

5. Ask: "Does this capture what matters? Anything to adjust?"
   Adjust based on response.

6. Write `<folder>/<slug>.md` (slug = title lowercased, spaces → hyphens, strip punctuation):

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
   <!-- 1–2 sentence summary of the speaker's main argument -->

   ## Key Insights
   - ...

   ## Key Moments
   | Time | What happens |
   |------|-------------|
   | [MM:SS] | ... |

   ## Quotable
   > "..."

   ## Chapters
   <!-- Only if the video has explicit chapters — list with timestamps and 1-line summary each -->

   ## Technical Terms
   <!-- Link to existing vault pages; flag new ones with "(→ /ingest?)" -->

   ## Open Questions
   <!-- What this raised that I want to dig into -->
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
4. Write `<folder>/<slug>.md` (slug = title lowercased, spaces → hyphens)
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
4. Write full markdown note — complete content, not a summary — with standard frontmatter
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
   Format: frontmatter + ## TL;DR (1 punchy sentence) + ## Key Points (3–5 bullets) + ## Related (leave placeholder comment)

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

   ## Summary
   <!-- 3–5 sentence overview -->

   ## Key Concepts
   <!-- Core ideas, definitions, components -->

   ## How It Works
   <!-- Architecture, mechanism, or process -->

   ## Use Cases
   <!-- Where this is applied, especially in AI/data engineering -->

   ## Current State (as of <TODAY>)
   <!-- Latest tools, models, frameworks, benchmarks -->

   ## Trade-offs
   <!-- Pros, cons, when to use vs. alternatives -->

   ## Related Topics
   <!-- [[wikilinks to related vault notes]] -->

   ## Sources
   <!-- Links to papers, articles, docs used -->

   ## Open Questions
   <!-- What I still want to understand -->
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

   ## What I Already Know
   <!-- Pulled from existing vault notes -->

   ## Key Concepts
   <!-- Fill in as you study -->

   ## How It Works
   <!-- Mechanism, architecture, or process -->

   ## Use Cases
   <!-- Where and why this is used -->

   ## Code / Examples
   <!-- Snippets, commands, implementations -->

   ## Questions & Gaps
   <!-- What I still don't understand -->

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
