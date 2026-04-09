---
name: query
description: Answer a question using the wiki. Reads wiki/index.md first to find relevant pages, synthesizes an answer with wikilink citations, flags contradictions and gaps, and offers to file the answer back as a new wiki page. Supports multiple output formats.
---

# Query — Ask the Wiki

## Step 1: Detect output format

Infer from the question or ask if ambiguous:

| Signal | Output format |
|--------|--------------|
| Default | Synthesized answer inline |
| "as a note" / deep synthesis | File as `research/<slug>.md` |
| "compare" / "vs" / "difference between" | Markdown comparison table |
| "slides" / "presentation" / "deck" | Marp slide deck |
| "map" / "canvas" / "visual" | JSON canvas via `/json-canvas` skill |

---

## Step 2: Read wiki/index.md

Read `wiki/index.md` in full. From the one-line summaries, identify the **3–8 most relevant pages** for the question.

---

## Step 3: Read relevant pages

Read each identified page fully. While reading, note:
- Direct answers and supporting evidence
- Contradictions between pages (same concept, conflicting claims)
- Gaps (the wiki doesn't have an answer for part of the question)

---

## Step 4: Synthesize

Write the answer in the detected format with `[[wikilink]]` citations.

**Comparison table:**
```markdown
| Dimension | [[option-a]] | [[option-b]] |
|-----------|-------------|-------------|
```

**Marp slide deck:**
```markdown
---
marp: true
theme: default
---

# <Title>

---

## <Slide>
```

**Canvas:** Invoke `/json-canvas` with the synthesis as context.

---

## Step 5: Flag contradictions and gaps

```markdown
> [!warning] Contradiction
> [[page-a]] says X, but [[page-b]] says Y — worth resolving.

> [!question] Gap
> The wiki doesn't cover X. Search query to fill this: "..."
```

---

## Step 6: Offer to file back

If the answer is non-trivial:
> "This synthesis is worth saving. File it as a wiki page?"

If yes:
- Write to `research/<slug>.md` with standard research frontmatter
- Update `wiki/index.md`
- Append to `wiki/log.md`

---

## Step 7: Always log the query

```
## [DATE] query | <one-line question summary>
- Pages read: [[page1]], [[page2]], [[page3]]
- Format: <inline | note | table | slides | canvas>
- Filed back: [[research/slug]] (or "no")
```
