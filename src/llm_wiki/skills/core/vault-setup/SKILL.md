---
name: vault-setup
description: Interactive vault configurator. Asks the user to describe themselves in free text, then builds a personalized vault structure, CLAUDE.md, and slash commands.
---

# Vault Setup — Wiki Configurator

**Note:** Ensure you have already installed the core skills via `llm-wiki --install` before using this command.

Run from INSIDE the folder you want to become your vault.

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

## STEP 2 — Infer and preview, don't ask more questions

From their free-text answer, infer:
- Their role (business owner / developer / consultant / creator / student)
- Their primary pain point
- Scope (work only / work + personal / full life OS)
- Whether they have existing files

Then show a vault preview. Do NOT ask clarifying questions. Make smart inferences.

```
Here's your vault — ready to build when you are.

vault/
├── inbox/          Drop zone — everything new lands here first
├── daily/          Daily brain dumps and quick captures
├── [folder]/       [purpose based on their role]
├── [folder]/       [purpose based on their role]
├── [folder]/       [purpose based on their role]
├── projects/       Active work with status and next actions
└── archive/        Completed work — never deleted, just moved

Slash commands:
  /daily    — start your day with vault context
  /tldr     — save any session to the right folder
  /[role]   — [role-specific one-liner]

Type "build it" to create this, or tell me what to change.
```

Wait for confirmation before building anything.

## STEP 3 — Build after confirmation

Once they say "build it", "yes", "go", "looks good", or similar:

### Create folders
```bash
mkdir -p inbox daily [role folders] projects archive wiki
```

Role folder sets:
- Business Owner → `people/ operations/ decisions/`
- Developer → `research/ learning/ clients/`
- Consultant → `clients/ research/`
- Creator → `content/ research/ clients/`
- Student → `notes/ research/ learning/`

If personal scope → also `personal/`

### Create wiki infrastructure
```bash
# wiki/index.md — master catalog
cat > wiki/index.md << 'EOF'
# Wiki Index

**Updated:** YYYY-MM-DD

## Research

## Learning

## Data Engineering
EOF

# wiki/log.md — append-only activity log
cat > wiki/log.md << 'EOF'
# Wiki Log

Format: `## [YYYY-MM-DD] <operation> | <title>`
Operations: ingest | query | lint
Search: grep "^## \[" wiki/log.md | tail -10
EOF
```

### Write CLAUDE.md
Write directly to `CLAUDE.md` in the current directory:

```markdown
# CLAUDE.md — [inferred role]'s Second Brain

## Who I Am
[2-3 sentences based on what they told you — specific, personal, written in first person as Claude describing its owner]

## Vault Tool
vault-tool: [obsidian | foam | logseq | markdown]

## My Vault Structure
[folder tree with one-line purpose per folder]

## How I Work
[3-4 bullet points inferred from their answers — capture style, main pain point, scope, what they want from AI]

## Wiki Schema
- `wiki/index.md` — master catalog; read this first on any query
- `wiki/log.md` — append-only activity log
- Wikilink format: [[folder/slug]] (path-qualified)

## Context Rules
When I mention a decision → check [decisions or relevant folder] first
When I mention a person/client/project → look in [relevant folder]
When I ask you to write → read recent daily/ notes to match my voice
When something lands in inbox/ → ask if I want it sorted now

## Available Slash Commands
- /ingest     — add any source to the wiki
- /query      — ask the wiki; file answers back
- /lint       — full vault health-check
- /daily      — start the day
- /tldr       — end-of-session summary
- /graphbuild — rebuild wiki knowledge graph + search indexes
```

### Write memory.md
```markdown
# Memory

## Session Log
[Updated by Claude Code after each session]

## My Preferences
[Added as Claude learns them]
```

## STEP 4 — Context injection 

Once you have created the files: Do not ask context load question, `llm-wiki --install` handles it now.

## STEP 5 — Final output

```
Done. Your vault is live.

Your slash commands:
  /daily       — run this tomorrow morning
  /tldr        — run this at the end of any session
  /ingest      — add any source (URL, file, folder, topic)
  /query       — ask anything from your accumulated knowledge
  /lint        — full vault health-check
  /graphbuild  — rebuild search indexes after bulk changes
  /[role]      — [one liner]

Have files to import?
  Just say: /ingest inbox/
  Then: "Sort everything in inbox/ into the right folders"
```
