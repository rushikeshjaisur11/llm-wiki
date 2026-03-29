# Obsidian Claude Skills

Claude Code slash commands (skills) for an Obsidian second brain. Each skill is a prompt that Claude Code loads when you type `/skill-name` in the terminal — turning Claude into a vault-aware assistant that reads, writes, and organizes your notes.

## What This Is

These skills connect Claude Code to an Obsidian vault so you can:
- Start each day with your vault context surfaced
- Convert PDFs and documents to full markdown notes automatically
- Research topics and save structured notes with web sources
- Do weekly reviews without leaving the terminal
- Brain-dump freely and have Claude file everything in the right folder

They work by placing `SKILL.md` files inside `.claude/skills/<name>/` in your vault root. Claude Code discovers them automatically and exposes them as `/name` slash commands.

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

Or clone directly into your vault:

```bash
git clone https://github.com/rushikeshjaisur11/obsidian-claude-skills /tmp/ocs
cp -r /tmp/ocs/skills/* .claude/skills/
```

### 3. Add a CLAUDE.md to your vault root

Create `.../your-vault/CLAUDE.md` describing who you are and how your vault is structured. Claude reads this at the start of every session. See the [vault-setup](#vault-setup) skill to generate one automatically.

### 4. Wire it to Claude Code globally (optional but recommended)

Append to `~/.claude/CLAUDE.md`:

```
## My Personal Context
At the start of every session, read /absolute/path/to/your-vault/CLAUDE.md for context about who I am, my work, and my conventions.
```

Now every Claude Code session — anywhere on your machine — has your vault context.

## Skills

### `/daily`
**Start your day with vault context.**

Reads or creates today's daily note (`daily/YYYY-MM-DD.md`), checks `inbox/` for unprocessed files, surfaces carry-overs from the last 3 daily notes, and asks what you're working on today.

```
/daily
```

---

### `/study`
**Scaffold a structured study note on any topic.**

Searches your vault for existing related notes, then creates a new `learning/<topic>.md` with sections: What I Already Know, Key Concepts, How It Works, Use Cases, Code/Examples, Questions & Gaps, Resources, Related Notes.

```
/study
→ What topic are you studying? [LangGraph checkpointing]
```

---

### `/research`
**Web-search a topic + synthesize into a vault note.**

Searches your vault for existing knowledge, runs 3+ web searches for latest developments, synthesizes everything, and writes a full `research/<topic>.md` with Summary, Key Concepts, How It Works, Use Cases, Current State, Pros/Cons, Sources, and Open Questions. Cross-links to existing vault notes.

```
/research
→ What topic do you want to research? [MCP protocol internals]
```

---

### `/file-intel`
**Convert PDFs and documents in `inbox/` to full markdown notes.**

Processes any file type (PDF, PPTX, XLSX, DOCX, CSV, JSON, TXT) into a complete `.md` note — not a summary, the full content as structured markdown. Places each note in the right vault folder (`learning/`, `research/`, `data-engineering/`, `resources/`, `personal/`). Supports parallel or sequential processing. Asks to delete originals when done.

```
/file-intel
→ Which folder? [inbox/]
→ Parallel or sequential? [sequential]
```

---

### `/weekly`
**Weekly review — summarize the week, set next week's goals.**

Reads all daily notes from the past 7 days, writes a `daily/weekly-YYYY-MM-DD.md` with: What I Learned, What I Built, Blockers & Open Questions, Inbox Status, and Top 3 Goals for Next Week. Suggests filing any loose captures from daily notes.

```
/weekly
```

---

### `/braindump`
**Unstructured capture — Claude organizes it.**

You talk freely (messy is fine), Claude parses the content and categorizes it into: `learning/`, `research/`, `projects/`, `data-engineering/`, `personal/`, or today's `daily/` note. Shows the plan before writing anything.

```
/braindump
→ Go ahead — dump everything on your mind.
```

---

### `/tldr`
**Save a summary of this conversation to the vault.**

Extracts decisions made, key things to remember, and next actions from the current session. Saves as a clean markdown note to the most relevant folder based on topic. Also updates `memory.md` at the vault root with any new patterns or preferences.

```
/tldr
```

---

### `/vault-setup`
**Interactive vault configurator — builds a personalized vault from scratch.**

Asks one free-text question about who you are and what you want to track. Infers your role, pain points, and scope. Previews a vault structure before building anything. Creates folders, `CLAUDE.md`, and all skill files. Optionally wires vault context into Claude Code globally.

Run from inside the folder you want to become your vault:

```bash
cd ~/my-second-brain
claude
/vault-setup
```

---

### `/defuddle`
**Extract clean markdown from any web page.**

Uses [Defuddle CLI](https://github.com/kepano/defuddle) to strip navigation, ads, and clutter from web pages and return clean markdown. More token-efficient than `WebFetch` for articles, docs, and blog posts.

```
/defuddle
→ defuddle parse <url> --md
```

Requires: `npm install -g defuddle`

---

### `/obsidian-markdown`
**Write valid Obsidian Flavored Markdown.**

Reference skill for Obsidian-specific syntax: wikilinks (`[[Note]]`), embeds (`![[file]]`), callouts (`> [!note]`), frontmatter properties, tags, comments (`%%hidden%%`), LaTeX math, and Mermaid diagrams. Use when creating or editing `.md` files that need to render correctly in Obsidian.

---

## Vault Structure (Recommended)

```
your-vault/
├── inbox/              Drop zone — files land here, /file-intel processes them
├── daily/              Daily notes + weekly reviews
├── learning/           Study notes, course content, converted PDFs
├── research/           Deep dives, papers, /research output
├── data-engineering/   Work notes, pipelines, tool references
├── resources/          Bookmarks, cheatsheets, reference material
├── projects/           Active work with status and next actions
├── personal/           Goals, habits, reflections
├── archive/            Completed work — never deleted, just moved
├── scripts/            Utility scripts for automation
├── outputs/            Generated summaries, exports
├── CLAUDE.md           Your identity + vault conventions (read by Claude every session)
└── .claude/
    └── skills/         All skill files live here
```

## How Skills Work

Each skill is a `SKILL.md` file in `.claude/skills/<name>/`. When you type `/name` in Claude Code, it loads that file as a prompt and follows its instructions with access to all your vault files.

Skills can:
- Read and write files in your vault
- Search across folders with Glob/Grep
- Use WebSearch to pull live information
- Ask follow-up questions
- Remember preferences across sessions via memory files

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Obsidian (any version)
- For `/defuddle`: `npm install -g defuddle`
- For `/research`: Claude Code with web search enabled

## License

MIT
