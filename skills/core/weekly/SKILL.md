---
name: weekly
description: Weekly review — summarize the week's daily notes, surface key learnings, review active projects, set top 3 goals for next week. Run every Sunday.
---

# Weekly Review

## Step 1: Read the week's daily notes
Read all `daily/` notes from the past 7 days. Extract:
- Key learnings and study topics covered
- Work done and decisions made
- Blockers or unresolved items
- Anything captured but not yet sorted

## Step 2: Write the weekly summary
Create `daily/weekly-YYYY-MM-DD.md` (use the Sunday date):

```markdown
---
type: weekly-review
week-ending: YYYY-MM-DD
---

# Weekly Review — Week of YYYY-MM-DD

## What I Learned
<!-- Key study topics, concepts, breakthroughs -->

## What I Built / Did
<!-- Work completed, projects advanced -->

## Blockers & Open Questions
<!-- Things still unresolved -->

## Inbox Status
<!-- Files processed, notes sorted -->

## Top 3 Goals for Next Week
1.
2.
3.

## Notes to File
<!-- Captures from daily/ that need to move to the right folder -->
```

## Step 3: Suggest filing
If any captures in daily/ notes belong in learning/, research/, or data-engineering/, list them and ask: "Want me to move these to the right folders?"

## Step 4: Close out
Tell the user: "Week reviewed. Your top 3 for next week are saved."
