---
name: daily
description: Start the day with vault context. Read today's daily note or create one. Surface recent wiki activity, inbox status, and top priorities. Ask what we're working on.
---

# Daily — Start Your Day

## Step 1: Today's note

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

## Step 2: Recent wiki activity

Read `wiki/log.md`. Show the last 5 entries (lines matching `^## \[`) as:
> Recently: **[operation]** [title]

This surfaces what was ingested, queried, or linted recently so context carries across sessions.

## Step 3: Check inbox/

List files in `inbox/`. If any exist: "You have N file(s) in inbox/ — run `/ingest inbox/` to process them."

## Step 4: Surface priorities

Read the last 3 daily notes to surface any unresolved blockers or carry-overs. Show them concisely.

## Step 5: Ask

"What are we working on today?"
