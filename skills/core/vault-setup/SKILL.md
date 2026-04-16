---
name: vault-setup
description: Interactive vault configurator. Asks the user to describe themselves in free text, then builds a personalized vault structure, CLAUDE.md, and slash commands. Wires skills globally or locally with path patching. Works with Obsidian, VS Code + Foam, Logseq, or plain markdown.
---

# Vault Setup — Wiki Configurator

Run from INSIDE the folder you want to become your vault.

## STEP 0 — Wire up skills (run once per machine)

Skills live in `skills/` inside the llm-wiki repo. Python search tools live in `skills/_wiki/`.
This step copies them to where Claude Code can find them and patches vault paths.

### Ask two things:

1. **"What is the absolute path to your vault?"** (default: current working directory)
2. **"Install globally (recommended) or locally (vault-only)?"**
   - **Global** — skills go to `~/.claude/skills/`, available in every Claude Code session
   - **Local** — skills go to `<vault>/.claude/skills/`, only when running from inside the vault
3. **"Which vault tool do you use?"** (obsidian / foam / logseq / markdown)
   - If Obsidian: also install `skills/extras/obsidian/*`

### Then run the appropriate script:

**Bash / Git Bash (macOS, Linux, Windows Git Bash):**
```bash
VAULT_PATH="$(pwd)"
REPO_SKILLS="$VAULT_PATH/skills"     # assumes running from cloned repo / vault root

# Choose install destination
# Global:
DEST="$HOME/.claude/skills"
# Local:
# DEST="$VAULT_PATH/.claude/skills"

mkdir -p "$DEST"

# 1. Copy core skills
for skill_dir in "$REPO_SKILLS/core"/*/; do
  skill_name="$(basename "$skill_dir")"
  mkdir -p "$DEST/$skill_name"
  cp "$skill_dir/SKILL.md" "$DEST/$skill_name/SKILL.md"
done

# 2. Copy Obsidian extras (only if user chose Obsidian)
# for skill_dir in "$REPO_SKILLS/extras/obsidian"/*/; do
#   skill_name="$(basename "$skill_dir")"
#   mkdir -p "$DEST/$skill_name"
#   cp "$skill_dir/SKILL.md" "$DEST/$skill_name/SKILL.md"
# done

# 3. Copy Python search tools
mkdir -p "$DEST/_wiki"
cp "$REPO_SKILLS/_wiki/"*.py "$DEST/_wiki/"

# 4. Write vault path config for Python scripts
echo "$VAULT_PATH" > "$DEST/_wiki/.vault_path"

# 5. Patch all placeholders in copied files
SCRIPTS_PATH="$DEST/_wiki"
find "$DEST" -name "*.md" -exec sed -i "s|{{VAULT}}|$VAULT_PATH|g" {} +
find "$DEST" -name "*.md" -exec sed -i "s|{{SCRIPTS}}|$SCRIPTS_PATH|g" {} +

# 6. Register vault context globally (skip for local install)
mkdir -p "$HOME/.claude"
cat >> "$HOME/.claude/CLAUDE.md" << CTXEOF

## My Personal Context
At the start of every session, read $VAULT_PATH/CLAUDE.md for context about who I am, my work, and my conventions.
CTXEOF

# 7. Build initial search indexes (only if vault has content)
if [ -f "$VAULT_PATH/wiki/index.md" ]; then
  python "$SCRIPTS_PATH/build_graph.py"
  python "$SCRIPTS_PATH/build_routing.py"
  python "$SCRIPTS_PATH/build_index.py"
fi

echo "Done. Skills installed to $DEST"
```

**PowerShell (Windows):**
```powershell
$VAULT = (Get-Location).Path.Replace("\", "/")
$REPO_SKILLS = "$VAULT/skills"

# Choose install destination
# Global:
$DEST = "$env:USERPROFILE/.claude/skills"
# Local:
# $DEST = "$VAULT/.claude/skills"

# 1. Copy core skills
Get-ChildItem "$REPO_SKILLS/core" -Directory | ForEach-Object {
    $d = "$DEST/$($_.Name)"
    New-Item -ItemType Directory -Force $d | Out-Null
    Copy-Item "$($_.FullName)/SKILL.md" "$d/SKILL.md"
}

# 2. Copy Obsidian extras (only if user chose Obsidian)
# Get-ChildItem "$REPO_SKILLS/extras/obsidian" -Directory | ForEach-Object {
#     $d = "$DEST/$($_.Name)"
#     New-Item -ItemType Directory -Force $d | Out-Null
#     Copy-Item "$($_.FullName)/SKILL.md" "$d/SKILL.md"
# }

# 3. Copy Python search tools
$WIKI_DEST = "$DEST/_wiki"
New-Item -ItemType Directory -Force $WIKI_DEST | Out-Null
Copy-Item "$REPO_SKILLS/_wiki/*.py" $WIKI_DEST

# 4. Write vault path config
$VAULT | Set-Content "$WIKI_DEST/.vault_path" -NoNewline

# 5. Patch placeholders
$SCRIPTS_PATH = $WIKI_DEST.Replace("\", "/")
Get-ChildItem $DEST -Recurse -Filter "*.md" | ForEach-Object {
    (Get-Content $_.FullName -Raw) `
        -replace [regex]::Escape("{{VAULT}}"), $VAULT `
        -replace [regex]::Escape("{{SCRIPTS}}"), $SCRIPTS_PATH |
    Set-Content $_.FullName -NoNewline
}

# 6. Register vault context globally (skip for local)
Add-Content "$env:USERPROFILE\.claude\CLAUDE.md" "`n## My Personal Context`nAt the start of every session, read $VAULT/CLAUDE.md for context about who I am, my work, and my conventions."

# 7. Build initial search indexes (only if vault has content)
if (Test-Path "$VAULT/wiki/index.md") {
    python "$SCRIPTS_PATH/build_graph.py"
    python "$SCRIPTS_PATH/build_routing.py"
    python "$SCRIPTS_PATH/build_index.py"
}

Write-Host "Done. Skills installed to $DEST"
```

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

## STEP 4 — Context injection question

After building, ask:

```
One last thing — how do you want your vault context loaded into Claude Code?

1. Global (recommended) — adds one line to ~/.claude/CLAUDE.md so your vault 
   context loads automatically in every Claude Code session on this machine
2. Manual — I'll give you the line to paste into specific projects when you need it
3. Vault only — works automatically when you run claude from inside this folder
```

**If global:** Append to `~/.claude/CLAUDE.md` (create if needed):
```
## My Personal Context
At the start of every session, read [absolute vault path]/CLAUDE.md for context about who I am, my work, and my conventions.
```

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
