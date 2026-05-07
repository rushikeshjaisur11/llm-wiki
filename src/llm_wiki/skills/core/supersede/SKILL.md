---
name: supersede
description: Mark an old note as superseded by a new one. Adds superseded_by to old note, contradicts to new note, and a visible SUPERSEDED callout. Preserves history without deletion. Usage - /supersede <old-note> <new-note>
---

# Supersede — Mark a Note as Replaced by a Newer One

Vault root: `{{VAULT}}/`

## Usage

```
/supersede learning/langgraph/state-and-reducers learning/langgraph/state-v2
```

Or run without arguments to be prompted:
"Which note is the old (superseded) one?"
"Which note is the new (replacing) one?"

Both notes must already exist.

---

## Step 1: Read both notes

Read old note and new note fully.
Verify the supersession makes sense (new note covers the same topic with updated content).

Ask if unclear: "Is [[new-note]] a full replacement for [[old-note]], or a partial update?"
- Full replacement → proceed with supersession
- Partial update → suggest using `/refresh` on the old note instead

---

## Step 2: Update the old note

Add to frontmatter:
```yaml
superseded_by: "[[new-note]]"
confidence: low        # downgrade — this is now outdated
```

Insert at the very top of the body (after frontmatter):
```markdown
> [!warning] SUPERSEDED
> This note was replaced by [[new-note]] on YYYY-MM-DD. It is preserved for historical context. Do not rely on it for current implementation.
```

---

## Step 3: Update the new note

Add to frontmatter:
```yaml
contradicts:
- "[[old-note]]"
```

Insert a "See Also" or "Replaces" line in the new note's footer:
```markdown
> Replaces: [[old-note]] (deprecated YYYY-MM-DD)
```

---

## Step 4: Log

Append to `wiki/log.md`:
```
## [DATE] supersede | <Old note title> → <New note title>
- Old: [[folder/old-slug]] (now superseded)
- New: [[folder/new-slug]]
- Reason: <one-line summary of what changed>
```

---

## What NOT to do

- Do NOT delete the old note. It provides historical context and the LLM can reason about what changed.
- Do NOT use this for minor edits — use `/refresh` for that.
- Use this only when a note is genuinely replaced by a substantially different version.
