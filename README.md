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

### `/tip` — Note of the day

Picks a fresh, non-duplicate topic and files a rubric-compliant note into `tips/` at the vault root (filename format `<YYYY-MM-DD>-<slug>.md`). Topics come from two spaces: the tracked AI/LLM space (Claude/Claude Code workflow, LangGraph, LangChain, Google ADK, RAG, agents, vector DBs, new model/framework releases) and whatever the vault's `learning/` tree shows you're actually studying (e.g. a `learning/python/` folder surfaces topics like `asyncio` internals, new stdlib features, or notable PEPs). Language/library topics always include a runnable worked-example code snippet.

```
/tip
/tip <optional topic hint>
/tip --digest   # weekly roundup of the past 7 days' tips
```

Runs manually or via the daily automation; maintains its own `tips/index.md` hub.

---

### `/tldr` — End-of-session summary

Extracts decisions, key things to remember, and next actions from the current session. Saves to the most relevant folder. Asks if any insights are worth filing permanently to the wiki.

---

### `/vault-setup` — First-time vault configurator

One free-text question about who you are, then asks which markdown tool you use. Infers your role and pain points. Previews a vault structure before building anything. Creates folders, `wiki/index.md`, `wiki/log.md`, `CLAUDE.md`, and installs the right skill set for your vault tool. Wires vault context into Claude Code globally.

---

### `/refresh` — Re-verify a note against its source

Fetches the canonical `source:` URL for a note, diffs its current claims against the live docs, proposes updates, and bumps `last_verified`. Closes the staleness loop without deleting the original.

Use `--queue [N]` to surface the N most overdue notes for a spaced-repetition review session.

```
/refresh learning/langgraph/state-and-reducers
/refresh --queue 5
```

---

### `/uplift` — Bulk-fix low-scoring notes

Scans a folder for notes missing Quality Rubric v3 fields and auto-generates them: `> [!tldr]` callout, Mermaid diagram, worked example, `when-not-to-use` section, `see-also` wikilinks, version pins, and **recall prompts** (the highest-evidence retention intervention). Promotes `maturity:` tag when a note reaches full coverage.

```
/uplift learning/langgraph
/uplift learning/ai
```

---

### `/learningpath` — Generate a tiered reading plan

Searches the vault and analyses the knowledge graph to assign existing notes to **Foundations / Core / Advanced** tiers, with reading-time estimates, prerequisite-aware ordering, and freshness indicators. Saves the plan to `projects/` on request.

```
/learningpath understand vLLM internals
/learningpath build a RAG pipeline with reranking
```

---

### `/curriculum` — Goal-driven mastery curriculum

Give a learning goal; get a complete, research-backed day-by-day curriculum generated directly into your vault. Researches the topic via web search, library docs (context7), and existing vault notes, then writes an exhaustive concept tree and a full day-by-day schedule upfront. Days are generated on demand — one session at a time — so content stays current and nothing is wasted if you change pace.

Each day produces **1–3 atomic concept notes + a practical + a quiz/review file**, all scored against Quality Rubric v3. Deep days with multiple distinct concepts get one atomic note per concept (each self-contained with its own diagram, worked example, and recall prompts) instead of one bloated file.

**Invocation modes:**

| Command | Action |
|---------|--------|
| `/curriculum <goal>` | Research + generate full plan |
| `/curriculum next` | Generate next undone day (active curriculum) |
| `/curriculum next --slug <slug>` | Generate next day for a specific curriculum |
| `/curriculum day <N>` | Generate (or regenerate) a specific day |
| `/curriculum list` | Show all curricula + progress |
| `/curriculum resume <slug>` | Switch active curriculum |
| `/curriculum audit <slug>` | Check concept coverage vs. generated days |
| `/curriculum replan` | Rewrite plan from next undone day (adaptive) |
| `/curriculum grade <N>` | Run auto-grader for day N |
| `/curriculum export <slug>` | Export shareable bundle (no personal progress) |
| `/curriculum import <path>` | Import a shared curriculum bundle |
| `/curriculum today` | Show/generate today's scheduled day |

**Extended features:**
- **Calendar integration** — generates `.ics` with one event per day and `obsidian://` deep links; import once into Google Calendar / Outlook
- **Cross-curriculum prereq detection** — detects topic overlap with completed curricula; offers `--skip-known` to jump ahead
- **Auto-grading** — generates `graders/day-NN-grader.py` per practical; `/curriculum grade <N>` runs assertions and appends PASS/FAIL to the review file
- **Shareable export** — `/curriculum export` produces `SHARE.md` + `manifest.json` (concept tree, datasets, tool versions — no personal progress); `/curriculum import` reconstructs locally
- **Adaptive replanning** — `/curriculum replan` rewrites the plan from the next undone day based on "too easy / too hard / skipped" markers; archives old plan as `plan.v1.md`
- **Coverage audit** — `/curriculum audit` diffs the concept tree in `plan.md` against generated days and flags any promised concept not yet written

Curricula live in a top-level `curricula/<slug>/` folder, separate from atomic `learning/` notes.

---

### `/lint --quarterly` — Quarterly vault health report

Full-vault quality scan: staleness by topic class, confidence distribution, contradictions, orphans, dangling links, and learning folder structure gaps. Produces a dated `wiki/audit-YYYY-Q.md` dashboard. Run once per quarter.

```
/lint --quarterly
```

---

### `/supersede` — Mark a note as replaced

Marks an old note as `superseded_by:` a newer one, adds a visible `SUPERSEDED` callout, and cross-links both notes. Preserves history instead of deleting.

```
/supersede learning/langgraph/old-state-guide learning/langgraph/state-and-reducers
```

---

### `/promote` — Daily note → durable wiki

Extracts a snippet from a daily note and promotes it into the durable wiki (cookbook, troubleshooting, or a new concept note) with full frontmatter, version pin, and anonymization. Closes the daily → semantic memory loop.

---

### `/cookbook-add` — Add a recipe to a tech's cookbook

Appends a version-pinned, copy-paste ready code recipe to `learning/<tech>/cookbook.md`. Creates the file if it doesn't exist.

```
/cookbook-add langgraph
```

---

### Utility skills

| Skill | Purpose |
|-------|---------|
| `/defuddle` | Fetch any URL as clean markdown (used internally by `/ingest` and `/refresh`) |
| `/graphbuild` | Rebuild the wiki knowledge graph — includes stale and low-confidence subgraph reports |
| `/linkedin` | Draft a LinkedIn post from a topic, rough notes, or vault content; uses Unicode bold/italic that renders on LinkedIn |
| `/skill-optimizer` | Auto-improve any `SKILL.md` via a mutate → evaluate → promote loop; no API key required — runs natively through Claude Code |
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

## LLM Wiki v2 — Freshness & Anti-Rot System

All notes follow the **LLM Wiki v2** pattern: every claim carries provenance and a TTL. Skills enforce this automatically.

### Frontmatter schema (all notes)

```yaml
last_verified: 2026-05-08         # date claims were verified against source
confidence: high                  # high | medium | low
provenance: extracted             # extracted | inferred | ambiguous
maturity: seedling                # seedling | budding | evergreen — promote manually as you revise
verified_against_version: "langgraph==1.0.2"  # version tested against (library notes)
superseded_by: null               # [[note]] if this note is obsolete
contradicts: []                   # cross-links to conflicting notes
needs_split: false                # true if note covers more than one idea
```

### Quality Rubric v3 (typed)

Every note must pass the **7 universal fields** (U1–U7) plus type-specific add-ons:

| # | Field | Rule |
|---|-------|------|
| U1 | **Declarative title** | States a claim, not a noun: "LangGraph state is a TypedDict" not "State and Reducers" |
| U2 | **TL;DR callout** | `> [!tldr]` ≤ 3 lines, written in own words (not copy-pasted from source) |
| U3 | **Atomic** | One idea per note; flag `needs_split: true` if two ideas are present |
| U4 ⭐ | **Recall prompts** | 2–5 `> [!question]` / `> [!answer]-` Q&A pairs — highest-evidence retention intervention |
| U5 | **Provenance** | `source:` URL + `last_verified:` date in frontmatter |
| U6 | **See-also** | 3–5 `[[wikilinks]]` to related vault notes |
| U7 | **Maturity tag** | `maturity: seedling \| budding \| evergreen` in frontmatter |

**Type-specific add-ons** (only for the relevant `type:` value):

| `type:` | Required add-ons | Exempt from |
|---------|-----------------|-------------|
| `learning` (concept) | Mermaid diagram; "Why does this work?" section; when-not-to-use | version-pins |
| `cookbook` (procedure) | Version-pinned code (`# tested: lib==x.y`); `## What can go wrong`; prereq wikilink | diagram |
| `cheatsheet`, `reference` | Structured table; cross-link to a concept note for the "why" | diagram, worked-example |
| `tutorial` | Ordered `## Step N` headings; prerequisites declared; closing "You should now be able to…" | — |
| `index` (hub) | Orientation paragraph; mental-model diagram; reading order; sub-cluster annotations | worked-example, version-pins |

Run `/uplift <folder>` to auto-generate missing fields. Run `/lint` to score existing notes.

### TTL rules (staleness thresholds)

| Topic class | Tags | TTL |
|---|---|---|
| Framework APIs | langgraph, langchain, google-adk | 90 days |
| Cloud services | gcp, aws, vertexai | 90 days |
| Security / compliance | security | 60 days |
| Architecture concepts | architecture | 180 days |
| Foundations | dsa, sql, ml | 365 days |

`/lint` flags overdue notes. `/refresh` re-verifies against source. `/lint --quarterly` gives the full audit dashboard.

### Supersession protocol

When a note is outdated, `/supersede` marks it as `superseded_by:` the new note and adds a `SUPERSEDED` callout. Don't delete — history compounds.

### Daily → semantic memory loop

Daily notes capture raw ideas. `/promote` extracts and files them into the durable wiki (cookbook, troubleshooting, or concept notes) with full frontmatter and version pins.

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

```text
llm-wiki/
├── pyproject.toml         (Package metadata and dependencies)
└── src/
    └── llm_wiki/
        ├── cli.py         (Command-line wizard based on Typer+Rich)
        ├── skills/        (Skills bundled into the package)
        │   ├── _wiki/     Python search tools
        │   ├── core/      Installed for ALL vault types
        │   └── extras/    Installed for specific editors
```

---

## Setup

### 1. Install the LLM-Wiki package

To install the configuration wizard and search dependencies globally on your machine:

```bash
pip install llm-wiki-claude
```
*(Or if running from source: `pip install -e .`)*

### 2. Run the Install Wizard

Run the interactive wizard from your terminal to configure your new vault and wire up the skills:

```bash
llm-wiki --install
```

This will automatically prompt you for your absolute vault path, configure your Claude context globally, and copy the required skills into your `~/.claude/` directory correctly patched.

### 3. Start Claude Code and Build

Install Claude Code globally if you haven't already:
```bash
npm install -g @anthropic-ai/claude-code
```

Navigate to your vault folder and start Claude:
```bash
cd your-vault
claude
```

Type `/vault-setup` into Claude. It will ask about your occupation and automatically scaffold your data tracking systems (`inbox/`, `projects/`, `wiki/index.md`, `CLAUDE.md`, etc.).

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
