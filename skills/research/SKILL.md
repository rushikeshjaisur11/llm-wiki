---
name: research
description: Research a topic — web-search for latest info, pull existing vault notes, synthesize findings, and write a full structured MD note into research/. Use when the user wants to learn about or deep-dive into any topic.
---

# Research — Web Search + Vault Synthesis → MD Note

## Step 1: Get the topic
Ask: "What topic do you want to research?"

## Step 2: Search the vault
Search across `learning/`, `research/`, `data-engineering/` for any existing notes on the topic. Note what's already known.

## Step 3: Web search
Use WebSearch to find:
- Latest developments, papers, or tools on the topic
- Best explanations or tutorials
- Real-world use cases
- Any benchmarks or comparisons

Pull from at least 3 sources.

## Step 4: Synthesize and write
Create `research/<topic-slug>.md`:

```markdown
---
topic: <topic>
date: YYYY-MM-DD
type: research
tags: [research, <topic>]
---

# <Topic>

## Summary
<!-- 3-5 sentence overview -->

## Key Concepts
<!-- Core ideas, definitions, components -->

## How It Works
<!-- Architecture, mechanism, or process -->

## Use Cases
<!-- Where this is applied, especially in AI/data engineering -->

## Current State (as of YYYY-MM-DD)
<!-- Latest tools, models, frameworks, benchmarks -->

## Pros & Cons / Trade-offs

## Related Topics
<!-- [[wikilinks to related vault notes]] -->

## Sources
<!-- Links to papers, articles, docs used -->

## Open Questions
<!-- What I still want to understand -->
```

## Step 5: Cross-link
Check if any existing notes in `learning/` or `data-engineering/` should link to this new note. Add wikilinks where relevant.

## Step 6: Report back
Tell the user where the note was saved and ask: "Want to go deeper on any section?"
