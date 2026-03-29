---
name: daily
description: Start the day with vault context. Read today's daily note or create one. Check inbox/ for unprocessed files. Surface top priorities. Ask what we're working on.
---

# Daily — Start Your Day

## Step 1: Check for today's note
Look for `daily/YYYY-MM-DD.md` using today's date. If it exists, read it. If not, create it:

```markdown
# YYYY-MM-DD

## Top 3 Today
-

## Study / Learning
-

## Work
-

## Captures
-

## End of Day
-
```

## Step 2: Check inbox/
List files in `inbox/`. If any exist, tell the user: "You have N file(s) in inbox/ — want me to process them now?"

## Step 3: Surface priorities
Read the last 3 daily notes to surface any unresolved blockers or carry-overs. Show them concisely.

## Step 4: Ask
"What are we working on today?"
