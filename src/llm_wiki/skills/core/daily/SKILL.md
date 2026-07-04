---
name: daily
description: Start the day with vault context. Read today's daily note or create one. Surface top priorities. Ask what we're working on.
---

Read today's daily note at daily/YYYY-MM-DD.md (use today's actual date).
If it doesn't exist, create it with this template:

# [Today's Date]

## Top of Mind

## Today's Focus

## Notes

Then check the inbox/ folder and list any unprocessed files found.
Read the most relevant active project or client folder for context.
Summarize the top 3 priorities for today based on recent notes.

**Staleness nudge (non-blocking):**
Run a quick check: scan frontmatter of all files in `learning/` for `last_verified` > TTL (use TTL rules from `{{VAULT}}/SCHEMA.md`). Report only the top 3 most overdue notes as:
> "3 notes may be stale: [[langgraph/state-and-reducers]] (90 days overdue), … Run `/refresh <note>` to re-verify, or `/audit` for a full report."
Keep this brief — it's a nudge, not a full lint.

**Index reconcile nudge (non-blocking):**
If any file under `{{VAULT}}/learning/tips/` has a newer mtime than `{{VAULT}}/wiki/graph.json` (or `graph.json` doesn't exist), say:
> "New tips haven't been indexed yet. Run `/graphbuild` to refresh search/graph."
This catches tips written by the daily/weekly automation that skipped indexing.

Ask: "What are we working on today?"
