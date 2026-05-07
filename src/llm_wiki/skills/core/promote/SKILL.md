---
name: promote
description: Promote a snippet from a daily note into the durable wiki at the right learning path. Closes the daily-to-semantic memory loop. Usage - /promote <daily-note-date or snippet> <wiki-target>
---

# Promote — Daily Note → Durable Wiki

Vault root: `{{VAULT}}/`

Closes the daily → semantic memory loop. When you solve something at work or capture something useful in a daily note, this skill extracts it and files it as a durable wiki entry with full frontmatter and version pins.

## Usage

```
/promote 2026-05-08 learning/langgraph/cookbook
/promote 2026-05-08                         ← I'll ask what to extract and where
/promote "the retry pattern I wrote today"  ← describe the snippet; I'll find it
```

---

## Step 1: Find the snippet

If a date is given, read `daily/YYYY-MM-DD.md`.
If a description is given, search today's and recent daily notes.

Ask: "Which part of this daily note do you want to promote? (paste or describe it)"

Display the candidate snippet and ask: "Is this the right content?"

---

## Step 2: Determine the target

If no target was given, ask: "Where should this go? Options:"
- `learning/<tech>/cookbook.md` — a reusable recipe
- `learning/<tech>/troubleshooting.md` — an error fix
- `learning/<tech>/changelog.md` — a version / migration note
- `learning/<tech>/<concept>.md` — a concept explanation (new note)
- `research/<slug>.md` — a standalone research note

For `cookbook.md` and `troubleshooting.md`, the content is appended to the existing file.
For a new concept note, a full note is written.

**Apply anonymization rule**: replace employer name with "our platform" / "our workload" before writing.

---

## Step 3: Write the promoted content

**If appending to cookbook.md:**
```markdown
---
## <Recipe title> `YYYY-MM-DD`
> [!note] Context
> Promoted from daily note YYYY-MM-DD — <one sentence about what problem this solves>

```python
# tested: <lib>==<version>, python==3.12
<code here>
```

**Expected output:** <what this produces>
**Watch out for:** <gotcha if any>
```

**If appending to troubleshooting.md:**
```markdown
---
## Error: <error message or symptom> `YYYY-MM-DD`
**Root cause:** <why it happens>
**Fix:**
```<language>
<fix code>
```
**Version context:** <lib>==<version>
```

**If writing a new concept note:** use the full note template from `/ingest` study mode, with all LLM Wiki v2 frontmatter fields.

---

## Step 4: Update last_verified

If the promoted content relates to an existing note, bump that note's `last_verified` to today.

---

## Step 5: Log

Append to `wiki/log.md`:
```
## [DATE] promote | <snippet title>
- From: [[daily/YYYY-MM-DD]]
- To: [[learning/<tech>/cookbook]] or [[new-note]]
- Anonymized: yes/no
```
