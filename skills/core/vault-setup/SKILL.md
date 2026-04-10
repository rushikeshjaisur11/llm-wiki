---
name: vault-setup
description: First-time vault configurator. Asks who you are and which markdown tool you use, then builds a personalized vault structure, CLAUDE.md, and installs the right skill set. Works with Obsidian, VS Code + Foam, Logseq, or plain markdown.
---

# Vault Setup — First-Time Configurator

Run from INSIDE the folder you want to become your vault.

---

## STEP 1 — One question, free text

Display this message exactly, then wait for their response:

---

**Tell me about yourself in a few sentences so I can build your vault.**

Answer these in whatever order feels natural:

- What do you do for work?
- What falls through the cracks most — what do you wish you tracked better?
- Work only, or personal life too?
- Do you have existing files to import? (PDFs, docs, slides)

No need to be formal. A few sentences is enough.

---

## STEP 2 — Ask which vault tool they use

After reading their free-text answer, ask:

```
Which tool do you use for your vault?

1. Obsidian
2. VS Code + Foam
3. Logseq
4. Plain markdown (any editor)
5. Other
```

Store the choice as `vault_tool` (one of: obsidian | foam | logseq | markdown | other).

---

## STEP 3 — Infer and preview, don't ask more questions

From their free-text answer, infer:
- Their role (business owner / developer / consultant / creator / student)
- Their primary pain point
- Scope (work only / work + personal / full life OS)
- Whether they have existing files

Then show a vault preview. Do NOT ask clarifying questions. Make smart inferences.

```
Here's your vault — ready to build when you are.

📁 [current directory name]
├── wiki/           Master catalog (index.md) and activity log (log.md)
├── inbox/          Drop zone — everything new lands here first
├── daily/          Daily brain dumps and quick captures
├── [folder]/       [purpose based on their role]
├── [folder]/       [purpose based on their role]
├── research/       Deep dives and synthesized knowledge
├── projects/       Active work with status and next actions
└── archive/        Completed work — never deleted, just moved

Slash commands (all vaults):
  /ingest   — add any source to the wiki
  /query    — ask the wiki anything
  /lint     — vault health check
  /daily    — start your day with vault context
  /tldr     — save session summary to the right folder

Type "build it" to create this, or tell me what to change.
```

Wait for confirmation before building anything.

---

## STEP 4 — Build after confirmation

Once they say "build it", "yes", "go", "looks good", or similar:

### Create folders
```bash
mkdir -p wiki inbox daily research projects archive .claude/skills
```

Role folder additions:
- Business Owner → `mkdir -p people operations decisions`
- Developer → `mkdir -p learning data-engineering`
- Consultant → `mkdir -p clients`
- Creator → `mkdir -p content`
- Student → `mkdir -p learning`

If personal scope → also `mkdir -p personal`

### Create wiki infrastructure

Write `wiki/index.md`:
```markdown
# Wiki Index

**Updated:** YYYY-MM-DD

## Research
<!-- entries added by /ingest -->

## Learning
<!-- entries added by /ingest -->
```

Write `wiki/log.md`:
```markdown
# Wiki Log

Format: `## [YYYY-MM-DD] <operation> | <title>`
Operations: ingest | query | lint
Search: grep "^## \[" wiki/log.md | tail -10

---

## [YYYY-MM-DD] ingest | Wiki initialized
- Note: wiki/index.md, wiki/log.md
- Mode: vault-setup
```
(Replace `YYYY-MM-DD` with today's date.)

### Write CLAUDE.md

Write directly to `CLAUDE.md` in the current directory:

```markdown
# CLAUDE.md — [inferred role]'s Second Brain

## Who I Am
[2-3 sentences based on what they told you — specific, personal, written in first person]

## Vault Tool
vault-tool: <obsidian | foam | logseq | markdown | other>

## My Vault Structure
[folder tree with one-line purpose per folder]

## How I Work
[3-4 bullet points inferred from their answers]

## Wiki Schema
- `wiki/index.md` — master catalog; **read this first on any query**
- `wiki/log.md` — append-only activity log; `grep "^## \[" wiki/log.md | tail -10` for recent entries
- Every new note → add entry to `wiki/index.md` (newest-first within section)
- Every operation (ingest / query / lint) → append to `wiki/log.md`
- Wikilink format: `[[folder/slug]]` (path-qualified to avoid ambiguity)

## Context Rules
When I mention a topic → look in research/ and learning/ first, then synthesize
When I mention a project → check projects/ for existing context
When I ask you to write → read recent daily/ notes to match my voice
When something lands in inbox/ → ask if I want it sorted now

## Available Slash Commands
- /ingest     — add any source to the wiki (URL, file, folder, research topic, or study topic)
- /query      — ask the wiki anything; synthesizes from indexed pages; files answers back
- /lint       — full vault health-check: file system + wiki quality; reports then executes
- /daily      — start the day with vault context, recent wiki activity, and priorities
- /tldr       — save session summary to the right folder; offer to file insights to wiki
- /braindump  — quick unstructured capture, organized into the right folders
- /weekly     — review the week, summarize learnings, set next week's goals
```

---

## STEP 5 — Install skills (vault-type conditional)

### All vaults — install core skills
Copy the entire `skills/core/` directory from this repo into `.claude/skills/`:

```bash
# Run from inside the vault folder
cp -r <repo-path>/skills/core/* .claude/skills/
```

Or instruct the user manually:
```
Copy everything from skills/core/ in the repo into .claude/skills/ in your vault.
```

### Obsidian only — install extras + show manual step
```bash
cp -r <repo-path>/skills/extras/obsidian/* .claude/skills/
```

Then display:
```
One required step:
  Obsidian → Settings → General → Enable Command Line Interface
```

Then open the vault in Obsidian (OS-appropriate):
- **macOS:** `open -a Obsidian "$(pwd)"`
- **Windows:** `start "" "obsidian://open?vault=$(basename $(pwd))"`
- **Linux:** `xdg-open "obsidian://open?vault=$(basename $(pwd))"` or instruct user to open the folder as a new vault manually

Add to CLAUDE.md under "Vault Tool":
```
Using Obsidian — wikilinks use [[folder/slug]] format. Graph view, backlinks, and canvas output available.
obsidian-cli and obsidian-markdown skills are installed.
```

### VS Code + Foam only
Add to CLAUDE.md under "Vault Tool":
```
Using Foam — wikilinks resolve via Foam extension. Cmd/Ctrl+Click to navigate links.
Graph view available via Foam sidebar. Canvas output not available; use Mermaid diagrams instead.
```

### Logseq only
Add to CLAUDE.md under "Vault Tool":
```
Using Logseq — wikilinks work but avoid ((block-refs)) in Claude-written notes.
Stick to [[page links]]. Canvas output not available; use Mermaid diagrams instead.
```

### Plain markdown / other
No additional setup needed. All skills work with file-system operations only.

---

## STEP 6 — Wire globally (optional but recommended)

Ask:
```
How do you want your vault context loaded into Claude Code?

1. Global (recommended) — adds one line to ~/.claude/CLAUDE.md so your vault
   context loads in every Claude Code session on this machine
2. Vault only — works automatically when you run claude from inside this folder
3. Skip
```

**If global:** Append to `~/.claude/CLAUDE.md` (create if needed):
```
## My Personal Context
At the start of every session, read [absolute vault path]/CLAUDE.md for context about who I am, my work, and my conventions.
```

---

## STEP 7 — Final output

```
Done. Your vault is ready.

[If Obsidian] One manual step:
  Obsidian → Settings → General → Enable Command Line Interface

Your slash commands:
  /ingest   — add any source to the wiki (URL, file, research topic)
  /query    — ask the wiki anything
  /lint     — vault health-check
  /daily    — run this every morning
  /tldr     — run this at the end of any session

Have files to import?
  Drop them in inbox/ then run: /ingest inbox/
```
