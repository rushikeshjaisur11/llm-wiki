---
name: cookbook-add
description: Append a version-pinned recipe to learning/<tech>/cookbook.md. Creates cookbook.md if it doesn't exist. Usage - /cookbook-add <tech> (e.g. /cookbook-add langgraph)
---

# Cookbook Add — Append a Recipe to a Tech's Cookbook

Vault root: `{{VAULT}}/`

## Usage

```
/cookbook-add langgraph
/cookbook-add rag
/cookbook-add fastapi
```

A "recipe" is a copy-paste ready code pattern that solves a specific, common problem. Not a tutorial — just the working solution with minimal prose.

---

## Step 1: Get the recipe

Ask:
1. "What's the recipe title? (e.g. 'Retry agent on tool error', 'Stream SSE from FastAPI', 'Add memory to a LangGraph agent')"
2. "Paste the code or describe the pattern:"
3. "What version of `<tech>` was this tested against?"
4. "Any gotchas or common mistakes to warn about?"

Optionally ask:
5. "What's the source? (URL, your own code, or leave blank)"

Apply anonymization rule: replace employer name with "our platform".

---

## Step 2: Locate or create cookbook.md

Target: `{{VAULT}}/learning/<tech>/cookbook.md`

**If cookbook.md exists:** read it fully (to avoid duplicates and to match existing style).
**If cookbook.md doesn't exist:** create it with this header:

```markdown
---
title: <Tech> Cookbook
created: <TODAY>
updated: <TODAY>
last_verified: <TODAY>
confidence: high
provenance: extracted
tags:
- <tech>
- cookbook
type: cookbook
related:
- '[[learning/<tech>/index]]'
- '[[learning/<tech>/production]]'
---

# <Tech> Cookbook

> Copy-paste recipes for common <Tech> tasks. Every snippet is version-pinned and tested. For production architecture patterns, see [[learning/<tech>/production]].

---
```

---

## Step 3: Check for duplicates

Scan existing cookbook.md for a recipe with the same title or very similar functionality. If found, ask: "This looks similar to an existing recipe — update it or add a new one?"

---

## Step 4: Append the recipe

Append to the end of cookbook.md:

```markdown
## <Recipe Title> `<TODAY>`

> [!note] Use case
> <One sentence: when to use this pattern and what problem it solves>

```python
# tested: <lib>==<version>, python==3.12
<code here>
```

**Expected output:**
```
<what running this produces — concrete, not "see above">
```

**Watch out for:** <gotcha — one bullet per issue, omit section if none>

**Source:** <URL or "from real work">

---
```

---

## Step 5: Update cookbook.md frontmatter

Bump `updated: <TODAY>` in the frontmatter.

---

## Step 6: Log

Append to `wiki/log.md`:
```
## [DATE] cookbook-add | <Recipe title> → learning/<tech>/cookbook
- Tech: <tech>
- Tested version: <version>
- Source: <url or "real work">
```
