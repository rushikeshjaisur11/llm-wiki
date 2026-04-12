---
name: query
description: Answer a question using the wiki. Reads wiki/index.md first to find relevant pages, synthesizes an answer with wikilink citations, flags contradictions and gaps, and offers to file the answer back as a new wiki page. Use when asking anything that should be answered from accumulated knowledge. Supports multiple output formats.
---

# Query — Ask the Wiki

Vault root: `C:/Users/rushi/llm-wiki/`

## Step 1: Detect output format

Infer from the question or ask if ambiguous:

| Signal | Output format |
|--------|--------------|
| Default | Synthesized answer inline (not filed) |
| "as a note" / deep synthesis | File as `research/<slug>.md` |
| "compare" / "vs" / "difference between" | Markdown comparison table |
| "slides" / "presentation" / "deck" | Marp slide deck in `research/<slug>.md` |
| "map" / "canvas" / "visual" | JSON canvas via `/json-canvas` skill |

---

## Step 2: Graph routing (2-stage)

**Check for graph first.** If `wiki/graph.json` does not exist → fall back to reading `wiki/index.md` in full and picking 3–8 pages by keyword match (old behaviour).

If `wiki/graph.json` exists:

### Stage 1 — Community match (reads `wiki/graph.json` only)

Read `wiki/graph.json`. Tokenise the question (lowercase, split on spaces/punctuation, strip stopwords).
For each community in `communities`:
- `keyword_score` = # question tokens matching `community.keywords`
- `label_score`   = # question tokens matching words in `community.label` (lowercase)
- `total = keyword_score + label_score`

Take the **top 1–2 communities** (total > 0). If tied, take both. If no community scores > 0 → fall back to `wiki/index.md`.

### Stage 2 — Node scoring within community (reads `wiki/graph/nodes/<c>.json`)

For each matched community, read `wiki/graph/nodes/<community>.json`.
Score each node:
- `tag_score`     = # question tokens matching `node.tags`   (weight ×3)
- `title_score`   = # question tokens appearing in `node.title` or the path segments of `node.id`  (weight ×2)
- `summary_score` = # question tokens appearing in `node.summary` (weight ×1)
- `total = tag_score * 3 + title_score * 2 + summary_score`

Sort descending. Take **top 5 candidates** across all matched communities.

> Note: many notes lack explicit summary sections — `title_score` and `tag_score` are the primary signals.

### Stage 2b — BFS neighbour expansion (reads `wiki/graph/edges.json`, optional)

If top candidates < 3 OR top score == 0:
- Read `wiki/graph/edges.json`
- For each top candidate, add its 1-hop neighbours that share ≥1 question token in their tags
- Cap the final set at 8 nodes

→ The resulting node IDs are the pages to read in Step 3.

---

## Step 3: Read relevant pages

Read each identified page fully. While reading, note:
- Direct answers and supporting evidence
- Context, background, examples
- Contradictions between pages (same concept, conflicting claims)
- Gaps (question requires knowledge the wiki doesn't have)

---

## Step 4: Synthesize

Write the answer in the detected format:

**Inline answer (default):**
Synthesize with `[[wikilink]]` citations — cite specific pages, not just topics. Be direct: lead with the answer, support with evidence.

**Comparison table:**
```markdown
| Dimension | [[option-a]] | [[option-b]] |
|-----------|-------------|-------------|
| ...       | ...         | ...         |
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
...
```

**Canvas:** Invoke `/json-canvas` with the synthesis as context to build a visual map.

---

## Step 5: Flag contradictions and gaps

Add callouts inline where relevant:

```markdown
> [!warning] Contradiction
> [[page-a]] says X, but [[page-b]] says Y — worth resolving.

> [!question] Gap
> The wiki doesn't cover X. Search query to fill this: "..."
```

---

## Step 6: Offer to file back

If the answer is non-trivial (more than a quick fact):
> "This synthesis is worth saving. File it as a wiki page?"

If yes:
- Write to `research/<slug>.md` with standard research frontmatter
- Update `wiki/index.md` (add entry)
- Append to `wiki/log.md`

---

## Step 7: Always log the query

Append to `wiki/log.md` regardless of whether the answer was filed:
```
## [DATE] query | <one-line question summary>
- Pages read: [[page1]], [[page2]], [[page3]]
- Format: <inline | note | table | slides | canvas>
- Filed back: [[research/slug]] (or "no")
```
