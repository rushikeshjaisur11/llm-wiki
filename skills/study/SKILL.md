---
name: study
description: Load a topic, pull all related notes from the vault, scaffold a new structured study note in learning/. Use when starting a study session on any AI/ML or data engineering topic.
---

# Study — Scaffold a Study Note

## Step 1: Get the topic
Ask: "What topic are you studying?"

## Step 2: Search the vault
Search across `learning/`, `research/`, `data-engineering/`, and `daily/` for any existing notes related to the topic. List what you find.

## Step 3: Create the study note
Write a new note at `learning/<topic-slug>.md` with this structure:

```markdown
---
topic: <topic>
date: YYYY-MM-DD
status: in-progress
tags: [study, <topic>]
---

# <Topic>

## What I Already Know
<!-- Pull from existing vault notes -->

## Key Concepts
<!-- Fill in as you study -->

## How It Works
<!-- Mechanism, architecture, or process -->

## Use Cases
<!-- Where and why this is used -->

## Code / Examples
<!-- Snippets, commands, implementations -->

## Questions & Gaps
<!-- What I still don't understand -->

## Resources
<!-- Links, papers, courses -->

## Related Notes
<!-- [[wikilinks to related vault notes]] -->
```

## Step 4: Show and ask
Show the created note path. Ask: "Ready to start — what do you want to fill in first?"
