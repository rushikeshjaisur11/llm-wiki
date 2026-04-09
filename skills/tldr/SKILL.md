---
name: tldr
description: Save a summary of this conversation to the vault. Key decisions, things to remember, next actions. Store in the right folder automatically. Offer to file key insights back to the wiki.
---

Summarize this conversation:
1. What was decided or figured out
2. Key things to remember
3. Next actions (if any)

Format as a clean markdown note with today's date in the title.
Save to the most relevant folder based on the topic discussed.
- Research / deep dives → research/
- Learning / tutorials → learning/
- Work / engineering → projects/ or data-engineering/
- Personal → personal/
- General → daily/ with today's date

Also update `memory.md` at the vault root with any new patterns or preferences discovered in this session.

Finally, ask: **"Any insights from this session worth adding to the wiki permanently?"**
If yes: write a concise note to `research/` or `learning/`, update `wiki/index.md` with the new entry, and append to `wiki/log.md`:
```
## [DATE] ingest | <insight title>
- Note: [[folder/slug]]
- Source: tldr session summary
```
