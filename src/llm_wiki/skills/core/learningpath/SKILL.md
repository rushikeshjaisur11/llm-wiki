---
name: learningpath
description: Generate a tiered reading plan from a learning goal. Searches the vault, analyses the knowledge graph to assign notes to Foundations / Core / Advanced tiers with reading-time estimates and wikilinks. Saves the plan to projects/ on request.
---

# Learning Path — Structured Reading Plan from Goal

Vault root: `{{VAULT}}/`

---

## Step 1: Receive the learning goal

The argument to `/learningpath` is the free-form goal string.

Examples:
- `/learningpath understand vLLM internals`
- `/learningpath learn Kafka architecture`
- `/learningpath build a RAG pipeline with reranking`

If no argument was given, ask: "What do you want to learn?"

---

## Step 2: Run learningpath.py

```
python {{SCRIPTS}}/learningpath.py "<goal>" --top 10
```

Flags:
- Use `--top 15` for broad goals with many relevant notes (e.g. "full data engineering stack", "complete RAG system").
- Use `--top 6` for narrow/specific goals (e.g. "RoPE position encoding", "DLT schema evolution").
- Add `--debug` if the output looks wrong — it prints search stage details to stderr.

If the output contains `"error"` key or prints `NO_RESULTS`:
> "No notes matched that goal. Try broader keywords, or use `/ingest` to add relevant material first."

The JSON output has three tiers:
- **foundations** — prerequisite notes (referenced by the core topic or by many candidates)
- **core** — most directly relevant notes for the goal
- **advanced** — notes that extend or build on the core topic

Each entry: `id`, `title`, `summary`, `tags`, `reading_time` (minutes).

---

## Step 3: Present the learning path

Format the JSON output as a readable plan:

```
## Learning Path: "<goal>"
*N notes · ~X hours Y min total*

### 🧱 Foundations — learn these first
1. [[node_id|Title]] · ~N min
   *Why first*: one sentence from summary explaining prerequisite relationship

### 🎯 Core — main subject
2. [[node_id|Title]] · ~N min
   *Why*: one sentence from summary

### 🚀 Advanced — extend your knowledge
3. [[node_id|Title]] · ~N min
   *Why*: one sentence from summary
```

Rules:
- Use `[[wikilinks]]` for every note
- Write a one-line *Why* from the note's summary field — make it specific, not generic
- If a tier is empty, omit that section entirely (no "No foundations found" clutter)
- Group reading time as hours + minutes when total exceeds 60 min (e.g. "~2 h 15 min")

---

## Step 4: Optional — read and synthesise

If the user asks for a quick overview before diving in:

1. Read the first **Core** note and the first **Foundations** note (if any) using the Read tool.
2. Write a 3–5 sentence synthesis: what the goal involves, what the vault covers, any notable gaps.
3. Flag gaps:
   ```
   > [!question] Gap
   > The vault doesn't cover X. Suggested search: "..."
   ```

---

## Step 5: Optional — save the plan

If the user says yes to saving:

1. Slug = goal lowercased, spaces → hyphens, punctuation stripped, max 60 chars.
   Example: "understand vLLM internals" → `vllm-internals`

2. Write to `projects/learningpath-<slug>.md` with this template:

```markdown
---
title: "Learning Path: <goal>"
created: <TODAY YYYY-MM-DD>
tags: [learning-path, <topic-tag>]
status: not-started
---

# Learning Path: <goal>

## 🧱 Foundations
<!-- prerequisite notes -->

## 🎯 Core
<!-- main subject notes -->

## 🚀 Advanced
<!-- extension notes -->

## Progress

| Note | Status |
|------|--------|
| [[note-id\|Title]] | ☐ |

## Reflections

<!-- notes as you work through the plan -->
```

3. Add an entry to `wiki/index.md` under a `## Learning Paths` section (create the section if missing):
   ```
   - [[projects/learningpath-<slug>]] — <goal> (YYYY-MM-DD)
   ```

---

## Step 6: Always log to wiki/log.md

Append regardless of whether the plan was saved:

```
## [YYYY-MM-DD] learnpath | <goal>
- Tiers: <N> foundations · <N> core · <N> advanced · ~<N> min total
- Saved: projects/learningpath-<slug>.md (or "no")
```
