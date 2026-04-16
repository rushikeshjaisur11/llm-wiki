# LLM Wiki

Claude Code slash commands that build and maintain a persistent, compounding knowledge base in any markdown vault.

Works with **Obsidian**, **VS Code + Foam**, **Logseq**, or any directory of markdown files.

Inspired by the [Andrej Karpathy’s LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

## The idea

Most LLM + notes setups work like RAG: upload files, retrieve chunks at query time, generate an answer. Nothing accumulates. Ask a question tomorrow and Claude re-derives it from scratch.

This is different. Claude maintains a **persistent wiki** — a `wiki/index.md` that catalogs every page and a `wiki/log.md` that records every operation. When you add a source, Claude reads it, extracts key insights, writes a note, and updates cross-links across related pages. When you ask a question, Claude reads the index first, finds the relevant pages, and synthesizes from compiled knowledge — not raw retrieval.

The wiki gets richer with every source you add and every question you ask. Cross-references are already there. Contradictions have been flagged. The synthesis already reflects everything you've read.

---

## Skills

### `/ingest` — Add any source to the wiki

The unified entry point for all knowledge ingestion.

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

Supports output formats: inline answer, comparison table, Marp slide deck, Mermaid diagram (all vaults), JSON canvas (Obsidian only).

---

### `/lint` — Full vault health-check

Scans the vault and reports on both **file system** and **wiki knowledge** health. Report first, execute after your confirmation.

File system: loose root files, unprocessed inbox, misplaced files, duplicates, empty folders, junk file types.

Wiki knowledge: pages missing from index, broken wikilinks, orphan pages (nothing points to them), concept stubs (concepts mentioned in prose but lacking their own page), contradictions between pages, actionable search suggestions for gaps.

For Obsidian users, broken links and orphan detection use `obsidian-cli` natively (most accurate — handles aliases and renamed files). All other vaults use Grep.

Writes `wiki/lint-YYYY-MM-DD.md` with full findings.

---

### `/daily` — Start your day

Reads or creates today's daily note, shows the last 5 wiki log entries (what was ingested/queried/linted recently), checks inbox for unprocessed files, surfaces carry-overs from recent days, and asks what you're working on.

---

### `/tldr` — End-of-session summary

Extracts decisions, key things to remember, and next actions from the current session. Saves to the most relevant folder. Asks if any insights are worth filing permanently to the wiki.

---

### `/vault-setup` — First-time vault configurator

One free-text question about who you are, then asks which markdown tool you use. Infers your role and pain points. Previews a vault structure before building anything. Creates folders, `wiki/index.md`, `wiki/log.md`, `CLAUDE.md`, and installs the right skill set for your vault tool. Wires vault context into Claude Code globally.

---

### Utility skills

| Skill | Purpose |
|-------|---------|
| `/defuddle` | Fetch any URL as clean markdown (used internally by `/ingest`) |
| `/graphbuild` | Rebuild the wiki knowledge graph from scratch — run after bulk ingests or when community assignments need refreshing |
| `/obsidian-cli` | Direct vault operations via Obsidian CLI (Obsidian only) |
| `/obsidian-markdown` | Reference for Obsidian-specific syntax: wikilinks, callouts, embeds, frontmatter (Obsidian only) |
| `/obsidian-bases` | Create and edit Obsidian Bases `.base` files — table/card views, filters, formulas (Obsidian only) |
| `/json-canvas` | Create and edit JSON Canvas `.canvas` files — visual maps, mind maps, flowcharts (Obsidian only) |

---

## Vault compatibility

| Feature | Obsidian | VS Code + Foam | Logseq | Plain markdown |
|---------|----------|----------------|--------|----------------|
| Core skills (ingest, query, lint, daily, tldr, defuddle, graphbuild, vault-setup) | ✓ | ✓ | ✓ | ✓ |
| `[[folder/slug]]` wikilinks | ✓ (graph-clickable) | ✓ (Foam resolves) | ✓ | ✓ (text only) |
| YAML frontmatter | ✓ (Properties panel) | ✓ | ✓ | ✓ |
| `> [!callout]` syntax | ✓ (native) | degrades gracefully | degrades gracefully | degrades gracefully |
| Canvas output in /query | ✓ (JSON canvas) | Mermaid fallback | Mermaid fallback | Mermaid fallback |
| Lint broken links | ✓ (`obsidian unresolved`) | ✓ (Grep) | ✓ (Grep) | ✓ (Grep) |
| Lint orphan detection | ✓ (`obsidian backlinks`) | ✓ (Grep) | ✓ (Grep) | ✓ (Grep) |
| obsidian-cli skill | ✓ | — | — | — |
| obsidian-bases skill | ✓ | — | — | — |
| json-canvas skill | ✓ | — | — | — |

---

## Wiki infrastructure

Two files anchor the wiki. `/vault-setup` creates these automatically, or create them manually.

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

## Search architecture

Query routing is handled by Python scripts in `skills/_wiki/` — Claude reads zero routing files. The 3-stage pipeline:

1. **Stage 0 — Community match** (`routing.md`, O(1), ~500 bytes): tokenise query, match against community keywords
2. **Stage 1 — FTS5 BM25** (`search.db`, Porter stemming): full-text search with community pre-filter, PMI synonym expansion, fuzzy correction
3. **Stage 2 — sqlite-vec re-rank** (optional): semantic re-ranking if `sqlite-vec` + `sentence-transformers` are installed

**Scaling:** 1k notes ~5ms | 10k notes ~10ms | 100k notes ~30ms

**Token cost per query:** ~100 bytes (just returned paths) vs 4-8 KB with direct file reads.

Scripts:
- `search.py` — main search entry point (used by `/query`, `/ingest`)
- `build_graph.py` — knowledge graph builder (community detection, edges)
- `build_routing.py` — 2-tier compact Markdown routing index
- `build_index.py` — SQLite FTS5 index + PMI synonym builder

All scripts support `--update <path>` for O(1) incremental updates and full rebuild mode.

---

## Repo structure

```
skills/
├── _wiki/              Python search tools (copied during setup)
│   ├── build_graph.py
│   ├── build_routing.py
│   ├── build_index.py
│   └── search.py
├── core/               Installed for ALL vault types
│   ├── ingest/
│   ├── query/
│   ├── lint/
│   ├── daily/
│   ├── tldr/
│   ├── defuddle/
│   ├── graphbuild/
│   └── vault-setup/
└── extras/
    └── obsidian/       Installed ONLY for Obsidian users
        ├── obsidian-cli/
        ├── obsidian-markdown/
        ├── obsidian-bases/
        └── json-canvas/
```

---

## Setup

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Run `/vault-setup` (recommended)

From inside your vault folder:

```bash
cd your-vault
claude
```

Then type `/vault-setup`. It will ask who you are and which tool you use, then build everything.

### 3. Manual setup (alternative)

```bash
VAULT="$(pwd)"
DEST="$HOME/.claude/skills"    # or "$VAULT/.claude/skills" for local

# Install core skills
cp -r path/to/llm-wiki/skills/core/* "$DEST/"

# Obsidian only — also install extras
cp -r path/to/llm-wiki/skills/extras/obsidian/* "$DEST/"

# Install Python search tools
mkdir -p "$DEST/_wiki"
cp path/to/llm-wiki/skills/_wiki/*.py "$DEST/_wiki/"
echo "$VAULT" > "$DEST/_wiki/.vault_path"

# Patch placeholders in all SKILL.md files
find "$DEST" -name "*.md" -exec sed -i "s|{{VAULT}}|$VAULT|g" {} +
find "$DEST" -name "*.md" -exec sed -i "s|{{SCRIPTS}}|$DEST/_wiki|g" {} +
```

Create `wiki/index.md` and `wiki/log.md` with the templates above.

Create `CLAUDE.md` with at minimum:
```markdown
# CLAUDE.md

## Who I Am
[2-3 sentences about your role and what this vault tracks]

## Vault Tool
vault-tool: obsidian   <!-- obsidian | foam | logseq | markdown | other -->

## Wiki Schema
- `wiki/index.md` — master catalog; read this first on any query
- `wiki/log.md` — append-only activity log
- Wikilink format: [[folder/slug]] (path-qualified)

## Available Commands
- /ingest      — add any source to the wiki
- /query       — ask the wiki; file answers back
- /lint        — full vault health-check + cleanup
- /daily       — start the day
- /tldr        — end-of-session summary
- /graphbuild  — rebuild wiki knowledge graph + search indexes
```

Build search indexes (after vault has content):
```bash
python "$DEST/_wiki/build_graph.py"
python "$DEST/_wiki/build_routing.py"
python "$DEST/_wiki/build_index.py"
```

### 4. Wire globally (optional but recommended)

Append to `~/.claude/CLAUDE.md`:

```
## My Personal Context
At the start of every session, read /absolute/path/to/your-vault/CLAUDE.md for context about who I am, my work, and my conventions.
```

Now every Claude Code session on your machine has your vault context.

### 5. Enable defuddle (optional)

Required for URL ingestion:

```bash
npm install -g defuddle
```

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Python 3.10+ (for search scripts)
- PyYAML (`pip install pyyaml`)
- Any markdown vault (Obsidian, VS Code + Foam, Logseq, or plain files)
- For `/ingest` URL mode: `npm install -g defuddle`
- For `/ingest research:` mode: Claude Code with web search enabled
- For Obsidian `/lint` native accuracy: Obsidian CLI enabled (Settings → General → Command Line Interface)
- Optional: `networkx` for structural community refinement in graph builder
- Optional: `sqlite-vec` + `sentence-transformers` for Stage 2 semantic re-ranking

## License

MIT
