# Obsidian Claude Skills

Claude Code slash commands for an LLM-maintained Obsidian wiki. Instead of re-deriving knowledge on every question, Claude incrementally builds and maintains a persistent wiki — indexing every source you add, cross-linking related pages, and synthesizing answers from accumulated knowledge rather than scratch.

Inspired by the [LLM Wiki pattern](https://github.com/rushikeshjaisur11/obsidian-claude-skills/blob/master/llm-wiki.md).

## The idea

Most LLM + notes setups work like RAG: upload files, retrieve chunks at query time, generate an answer. Nothing is built up. Ask a question tomorrow and Claude re-derives it from scratch.

This is different. Claude maintains a **persistent wiki** — a `wiki/index.md` that catalogs every page and a `wiki/log.md` that records every operation. When you add a source, Claude reads it, extracts key insights, writes a note, and updates cross-links across related pages. When you ask a question, Claude reads the index first, finds the relevant pages, and synthesizes from compiled knowledge — not raw retrieval.

The wiki gets richer with every source you add and every question you ask. Cross-references are already there. Contradictions have been flagged. The synthesis already reflects everything you've read.

## Skills

### `/ingest` — Add any source to the wiki

The unified entry point for all knowledge ingestion. Replaces `/research`, `/study`, and `/file-intel`.

**Modes** (auto-detected from argument):
- `/ingest https://...` — fetch URL via defuddle, summarize, classify, write note
- `/ingest paper.pdf` — read file fully, write complete markdown note
- `/ingest inbox/` — batch-process folder with parallel subagents
- `/ingest research: <topic>` — web search + synthesize + write research note
- `/ingest study: <topic>` — scaffold study note from existing vault knowledge
- `/ingest` — asks what you're adding

Every mode ends the same way: note written → 3–5 related pages cross-linked → `wiki/index.md` updated → `wiki/log.md` appended.

---

### `/query` — Ask the wiki

Reads `wiki/index.md` first to find relevant pages, then synthesizes an answer with `[[wikilink]]` citations. Flags contradictions and knowledge gaps. Offers to file the answer back as a new wiki page so your explorations compound.

Supports output formats: inline answer, comparison table, Marp slide deck, JSON canvas.

---

### `/lint` — Full vault health-check

Scans the vault and reports on both **file system** and **wiki knowledge** health. Report first, execute after your confirmation.

File system: loose root files, unprocessed inbox, misplaced files, duplicates, empty folders, junk file types.

Wiki knowledge: pages missing from index, broken wikilinks, orphan pages (nothing points to them), concept stubs (concepts mentioned in prose but lacking their own page), contradictions between pages, actionable search suggestions for gaps.

Writes `wiki/lint-YYYY-MM-DD.md` with full findings. Replaces `/organize-vault`.

---

### `/daily` — Start your day

Reads or creates today's daily note, shows the last 5 wiki log entries (what was ingested/queried/linted recently), checks inbox for unprocessed files, surfaces carry-overs from recent days, and asks what you're working on.

---

### `/tldr` — End-of-session summary

Extracts decisions, key things to remember, and next actions from the current session. Saves to the most relevant folder. Asks if any insights are worth filing permanently to the wiki.

---

### `/weekly` — Weekly review

Reads all daily notes from the past 7 days. Writes a `daily/weekly-YYYY-MM-DD.md` with: What I Learned, What I Built, Blockers & Open Questions, and Top 3 Goals for Next Week.

---

### `/braindump` — Unstructured capture

You talk freely, Claude organizes. Parses your dump into categories (`learning/`, `research/`, `projects/`, `personal/`, today's daily note), shows the plan, and writes after confirmation.

---

### `/vault-setup` — First-time vault configurator

One free-text question about who you are. Infers your role and pain points. Previews a vault structure before building anything. Creates folders, `CLAUDE.md`, skill files, and wires vault context into Claude Code globally.

---

### Utility skills

| Skill | Purpose |
|-------|---------|
| `/defuddle` | Fetch any URL as clean markdown (used internally by `/ingest`) |
| `/obsidian-cli` | Direct vault operations via CLI (read, create, search, append, tasks) |
| `/obsidian-markdown` | Reference for Obsidian-specific syntax (wikilinks, callouts, embeds, frontmatter) |

---

## Wiki infrastructure

Two files anchor the wiki. Create these in your vault root before using `/ingest` and `/query`.

### `wiki/index.md`

The master catalog. Every page gets an entry here. Claude reads this first on every query.

```markdown
# Wiki Index

**Updated:** YYYY-MM-DD

## Research
- [[research/topic-name]] — one-line summary (YYYY-MM-DD)

## Learning
### Python
- [[learning/python/topic]] — one-line summary

## Data Engineering
- [[data-engineering/topic]] — one-line summary
```

### `wiki/log.md`

Append-only activity log. Records every ingest, query, and lint operation.

```markdown
# Wiki Log

Format: `## [YYYY-MM-DD] <operation> | <title>`
Operations: ingest | query | lint
Search: grep "^## \[" wiki/log.md | tail -10

---

## [2026-04-10] ingest | MCP Architecture Patterns
- Note: [[research/mcp-architecture]]
- Updated: [[research/mcp-tools]], [[learning/fastapi/async-patterns]]
- Mode: url
```

---

## Setup

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Copy skills to your vault

```bash
# From inside your Obsidian vault root
mkdir -p .claude/skills
cp -r path/to/obsidian-claude-skills/skills/* .claude/skills/
```

### 3. Create wiki infrastructure

```bash
mkdir -p wiki
```

Create `wiki/index.md` and `wiki/log.md` with the templates above.

### 4. Create CLAUDE.md

Add a `CLAUDE.md` at your vault root describing who you are, your vault structure, and the wiki schema. Minimum:

```markdown
# CLAUDE.md

## Who I Am
[2-3 sentences about your role and what this vault tracks]

## Vault Structure
[folder tree with one-line purpose per folder]

## Wiki Schema
- `wiki/index.md` — master catalog; read this first on any query
- `wiki/log.md` — append-only activity log
- Every new note → indexed in wiki/index.md (newest-first per section)
- Every operation → appended to wiki/log.md

## Available Commands
- /ingest  — add any source to the wiki
- /query   — ask the wiki; file answers back
- /lint    — full vault health-check + cleanup
- /daily   — start the day
- /tldr    — end-of-session summary
- /braindump — quick capture
- /weekly  — weekly review
```

### 5. Wire globally (optional but recommended)

Append to `~/.claude/CLAUDE.md`:

```
## My Personal Context
At the start of every session, read /absolute/path/to/your-vault/CLAUDE.md for context about who I am, my work, and my conventions.
```

Now every Claude Code session on your machine has your vault context.

### 6. Enable defuddle (optional)

Required for URL ingestion:

```bash
npm install -g defuddle
```

---

## Vault structure

```
your-vault/
├── wiki/
│   ├── index.md        Master catalog — updated on every ingest
│   └── log.md          Activity log — ingest | query | lint entries
├── inbox/              Drop zone — /ingest inbox/ to process
├── daily/              Daily notes + weekly reviews
├── research/           Deep dives, papers, /ingest research: output
├── learning/           Study notes, courses, /ingest study: output
├── data-engineering/   Pipelines, tools, schemas
├── projects/           Active work
├── personal/           Goals, habits, reflections
├── archive/            Completed work — never deleted, just moved
├── CLAUDE.md           Your identity + vault schema (read every session)
└── .claude/
    └── skills/         All skill files live here
```

---

## How skills work

Each skill is a `SKILL.md` file in `.claude/skills/<name>/`. When you type `/name` in Claude Code, it loads that file as a system prompt and follows its instructions with full access to your vault files, web search, and subagent spawning.

Skills can read and write files, search across folders, fetch URLs, spawn parallel subagents for batch work, and ask follow-up questions.

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Obsidian (any version)
- For `/ingest` URL mode: `npm install -g defuddle`
- For `/ingest research:` mode: Claude Code with web search enabled

## License

MIT
