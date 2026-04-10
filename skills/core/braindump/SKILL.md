---
name: braindump
description: Quick unstructured capture — user talks freely, Claude organizes the content into the right vault folders. No formatting required from the user.
---

# Braindump — Capture First, Organize Later

## Step 1: Capture
Say: "Go ahead — dump everything on your mind. Don't worry about structure."

Wait for the user's free-text input. It can be messy, incomplete, or a mix of topics.

## Step 2: Parse and categorize
Analyze the dump and split it into categories:
- Study notes / learnings → `learning/`
- Research ideas or findings → `research/`
- Work tasks or decisions → `projects/` or `data-engineering/`
- Personal todos or reflections → `personal/`
- Quick links or references → `resources/`
- Daily log items → `daily/YYYY-MM-DD.md`

## Step 3: Show the plan
Show the user how you've categorized their dump:

```
Here's where I'd put everything:

→ learning/   : [items]
→ research/   : [items]
→ daily/      : [items]
→ personal/   : [items]
```

Ask: "Does this look right, or do you want to move anything?"

## Step 4: Write the notes
After confirmation, append or create notes in each folder. For learning/research items, create a proper stub note. For daily items, append to today's note.

Tell the user: "Done — everything's filed."
