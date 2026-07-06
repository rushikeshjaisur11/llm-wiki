<!-- CONCEPT NOTE TEMPLATE — used by /curriculum B2b
     Filename: concepts.md (single-concept day) or concepts-0N-<topic-slug>.md (multi-concept day).
     Fill EVERY section fully. Atomicity guard (U3): if writing any section reveals a SECOND
     coherent idea, stop — split per B2a first, then complete both notes separately.
     Quality Rubric: U1–U7 + L1–L14 (all checked in B5 before marking day done). -->

---
title: "Day <N>: <declarative-claim-about-topic>"
day_label: "<short ≤6-word topic phrase — verbatim from plan.md Topic column>"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
last_verified: <YYYY-MM-DD>
confidence: high
provenance: generated+web
type: learning
maturity: seedling
needs_split: false
level: <easy|moderate|advanced>
tags: [curriculum/<slug>, day-<NN>, <topic-tags>]
curriculum: "[[curricula/<slug>/plan]]"
day: <N>
phase: <foundations|core|advanced|capstone>
prerequisites: ["[[curricula/<slug>/day-<NN-1>/concepts]]"]
related: []
source: <primary source URL>
---

# Day <N>: <declarative title — states a claim, not just a noun>

> [!tldr]
> Line 1: Core idea in one sentence (written in own words, not copy-pasted).
> Line 2: Why it matters for <goal>.
> Line 3: What you can do after today.

## Why this exists (motivation)

The problem this concept was invented to solve — 2–4 sentences, concrete.
Name the predecessor approach and its limitation; name what changed that made this concept necessary.
Example: "Before attention, sequence models had to compress all prior context into a fixed-size vector. As sequences grew, earlier tokens were forgotten. Attention let the decoder query all encoder states directly, learning which tokens matter for each output position."

## Intuition (mental model)

Plain-language analogy that builds the right mental picture before any formalism.
No jargon. Example: "Think of X as a Y that does Z."

## <Core concept section>

Explanation using concrete numbers. Never vague.

## Formal definition

Precise specification, pseudocode, or derivation. Use LaTeX for math (`$...$`).
Example:
$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

## Worked examples

> [!example] Example 1 — <short descriptor>
> End-to-end walkthrough with real numbers and real code output.
> Never use placeholder values like `<your_value>`.

```python
# tested: <lib>==<version>
<concrete runnable code>
```

**Output:**
```
<actual expected output>
```

> [!example] Example 2 — <short descriptor, different angle or edge case>
> Second walkthrough showing a variation or edge case.

```python
# tested: <lib>==<version>
<concrete runnable code>
```

**Output:**
```
<actual expected output>
```

## Why does this work?

Mechanistic explanation — the underlying reason, not just what it does.
Connect to the formal definition above.

## Cost & complexity

Time/space/compute cost and scaling behavior with real figures.
Example: "Scales as O(n²) in sequence length n; at n=512 the attention matrix is 512×512×4 bytes = 1 MB per head per layer. Memory doubles every time n doubles."
For non-quantitative concepts (design patterns, workflows): "No formal complexity bound — practical overhead is <describe latency / memory / operational impact with concrete figures where possible>."

## Diagram

```mermaid
<!-- process/architecture/flow diagram; use <br/> not \n in node labels -->
```

## Edge cases & boundary conditions

Where the concept itself breaks down or behaves unexpectedly under degenerate inputs or violated structural assumptions.
Distinct from runtime errors (those belong in practical.md "What can go wrong").

- Edge case 1 — condition → what happens
- Edge case 2 — condition → what happens

## Common misconceptions

| Misconception | Why it's wrong | Correct mental model |
|--------------|----------------|---------------------|
| "X means Y"  | Because ...    | Actually ...        |
| ...           | ...            | ...                 |

## Trade-offs vs alternatives

| Approach | When to prefer | Cost / downside |
|----------|---------------|-----------------|
| **<this technique>** | <conditions> | <limitations> |
| <alternative 1>      | <conditions> | <limitations> |
| <alternative 2>      | <conditions> | <limitations> |

## Variations & extensions

Named variants and frontier extensions — one line each.
Example: "Attention → Flash Attention (IO-aware recomputation, O(n) memory), Sparse Attention (strided/block patterns, sub-quadratic), Linear Attention (kernel approximation, O(n) time and space)."
If a variant is complex enough to warrant its own note, link it with [[wikilink]] and do not explain it inline here.

## When NOT to use this

- Anti-pattern 1 (specific condition)
- Anti-pattern 2 (specific condition)

## See also

- [[curricula/<slug>/day-<NN-1>/concepts]] — prior day
- [[curricula/<slug>/day-<NN+1>/concepts]] — next day
- [[<vault-note>]] — related vault concept

## Sources

- <Title of source 1> — <url> (accessed <YYYY-MM-DD>)
- <Title of source 2> — <url> (accessed <YYYY-MM-DD>)
(Add more; prefer primary sources: official docs, papers, changelogs)

## Recall prompts

> [!question] <One specific retrievable fact from today's concepts>

> [!answer]- <Concrete, specific answer — no vague generalities>

> [!question] When would you NOT use <X covered today>?

> [!answer]- <Specific anti-pattern with concrete condition>

> [!question] <Third prompt — mechanism or trade-off question>

> [!answer]- <Answer>

> [!question] <Fourth prompt — draw from a new depth section: exact cost bound, a specific edge case, or a named variant and its trade-off>

> [!answer]- <Answer: e.g. "O(n²) attention; Flash Attention reduces to O(n) memory via tiling" or "breaks when sequence length > context window; use sparse patterns">

> [!question] <Fifth prompt — connection to adjacent concept or prior day>

> [!answer]- <Answer>
