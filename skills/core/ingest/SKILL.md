---
name: ingest
description: Add any source to the wiki — URL, file, batch folder, research topic, or study topic. Always ends with the note written, cross-links added, wiki/index.md updated, and wiki/log.md appended. Use for all knowledge ingestion. Replaces /research, /study, and /file-intel.
---

# Ingest — Add to Wiki

## Mode detection

Detect from the argument passed:

| Argument | Mode |
|----------|------|
| `https://` or `http://` URL | URL |
| File path with extension (.pdf, .md, .docx, etc.) | Single file |
| Directory path (ends in `/` or is a folder) | Batch folder |
| `research: <topic>` | Research |
| `study: <topic>` | Study |
| Topic name only | Ask: "Research (web search) or Study (scaffold from vault)?" |
| No argument | Ask: "What are you adding? (URL, file, folder, or topic)" |

Vault root: read from CLAUDE.md or use the current working directory.

---

## URL mode

1. Use the `defuddle` skill to fetch and clean the URL into markdown
2. Write a 2–3 sentence synthesis of key insights → ask: "Does this capture what matters?"
3. Adjust based on response, then classify to vault folder:
   - `research/` — deep technical: papers, architecture, systems, LLMs, agents
   - `learning/` — guides, tutorials, how-tos, courses
   - (use other folders per your CLAUDE.md vault structure)
4. Write `<folder>/<slug>.md` (slug = title lowercased, spaces → hyphens) with standard frontmatter + content
5. If the article contains images: read text first, then view referenced images separately. For offline storage, download images to an `assets/` folder in your vault. Obsidian users: Settings → Files → Attachment folder path = "assets/", then use "Download attachments for current file" hotkey.
6. → **[Wiki Update]**

---

## Single file mode

1. Read the file completely
   - PDFs: read in 10-page chunks (`pages: "1-10"`, `"11-20"`, etc.) until all pages are read
   - Other formats: read in one call
2. Write 2–3 sentence synthesis → ask user to confirm emphasis
3. Classify to vault folder
4. Write full markdown note — complete content, not a summary — with standard frontmatter
5. → **[Wiki Update]**

---

## Batch folder mode

1. `Glob` all supported files in the folder: PDF, PPTX, XLSX, DOCX, CSV, JSON, MD, TXT
2. Send a **single message** with one `Agent` tool call per file (all in parallel):

   Subagent prompt template (fill in placeholders):
   ```
   Process a single file for a markdown wiki vault.
   File: <ABSOLUTE_PATH> | Date: <TODAY> | Vault root: <VAULT_ROOT>

   Step 1: Read the COMPLETE file.
   - PDFs: check total page count, read in 10-page chunks until all pages done.
   - Other formats: read in one call.
   - If unreadable/binary: return RESULT: SKIPPED | FILE: <name> | REASON: unreadable

   Step 2: Classify into a vault folder based on the CLAUDE.md vault structure.

   Step 3: Write full markdown source to: <vault-root>/<folder>/sources/<stem>.md
   The <stem> is filename without extension, spaces → underscores.
   Content must be COMPLETE — every word from original, verbatim. Not a summary.
   Use frontmatter: title, date, tags, source (original filename), type.

   Step 4: Write summary note to: <vault-root>/<folder>/<stem>.md
   Format: frontmatter + ## TL;DR (1 punchy sentence) + ## Key Points (3–5 bullets) + ## Related (placeholder comment)

   Step 5: Return exactly:
   RESULT: SUCCESS | FILE: <name> | FOLDER: <folder> | STEM: <stem> | TOPICS: <3-6 keywords>
   Or: RESULT: SKIPPED | FILE: <name> | REASON: <why>
   ```

3. Collect results. Cross-link notes that share topic keywords.
4. Ask: "Delete original files from the folder?" → if yes, remove each processed source file.
5. → **[Wiki Update — batch]**

---

## Research mode

1. Search vault for existing notes on the topic. Note what's already known.
2. `WebSearch` — at least 3 sources, prefer recent
3. Show 2–3 sentence synthesis → ask: "Anything to emphasize or cut?"
4. Write `research/<slug>.md`:

   ```markdown
   ---
   title: <Topic>
   date: <TODAY>
   tags: [<topic-tags>]
   type: research
   source-count: <N>
   related: []
   ---

   # <Topic>

   ## Summary

   ## Key Concepts

   ## How It Works

   ## Use Cases

   ## Current State (as of <TODAY>)

   ## Trade-offs

   ## Related Topics

   ## Sources

   ## Open Questions
   ```

5. → **[Wiki Update]**

---

## Study mode

1. Search vault for all existing notes on topic → extract into "What I Already Know"
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

   ## Key Concepts

   ## How It Works

   ## Use Cases

   ## Code / Examples

   ## Questions & Gaps

   ## Resources

   ## Related Notes
   ```

3. → **[Wiki Update]**
4. Ask: "Ready — what do you want to fill in first?"

---

## Wiki Update (runs after every mode)

1. Read `wiki/index.md` → find 3–5 pages sharing topics with the new note(s)
2. For each related page: append wikilink under `## Related` or `## See Also`; if contradiction found, add `> [!warning]` callout
3. Add new entry to `wiki/index.md` under the correct section (newest-first):
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
