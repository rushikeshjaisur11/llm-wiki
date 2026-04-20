---
name: query
description: Answer a question using the wiki. Runs search.py to find relevant pages (zero token cost), synthesizes an answer with wikilink citations, flags contradictions and gaps, and offers to file the answer back as a new wiki page. Use when asking anything that should be answered from accumulated knowledge. Supports multiple output formats.
---

# Query — Ask the Wiki

Vault root: `{{VAULT}}/`

## Step 1: Detect output format

Infer from the question or ask if ambiguous:

| Signal | Output format |
|--------|--------------|
| Default | Synthesized answer inline (not filed) |
| "as a note" / deep synthesis | File as `research/<slug>.md` |
| "compare" / "vs" / "difference between" | Markdown comparison table |
| "slides" / "presentation" / "deck" | Marp slide deck in `research/<slug>.md` |
| "map" / "canvas" / "visual" | Graph canvas via `export_canvas.py` |

---

## Step 2: Find relevant pages (Python search — zero token cost)

```
python {{SCRIPTS}}/search.py "<question keywords>" --top 5
```

- Output: vault-relative `.md` paths, one per line. Read only those files.
- If `NO_RESULTS`: fall back to reading `wiki/index.md` for keyword matching.
- Use `--debug` flag to see community scores and BM25 ranking on stderr.
- The script handles community routing, FTS5 BM25 search, PMI synonym expansion, and fuzzy correction internally — Claude reads zero routing files.

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

**Canvas:** Run the graph canvas exporter and open the result in Obsidian:
```
python {{SCRIPTS}}/export_canvas.py
```
This writes `wiki/graph.canvas` showing all vault notes grouped by community, colored by topic, with hub notes highlighted. Open in Obsidian to explore the knowledge graph visually.
If the user wants a focused canvas (only notes relevant to their query), filter by reading the community from `wiki/routing.md` and passing `--summary` first to identify the right community, then note which community files are most relevant.

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
