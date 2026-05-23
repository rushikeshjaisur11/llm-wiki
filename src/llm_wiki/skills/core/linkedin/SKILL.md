---
name: linkedin
description: Draft a LinkedIn post from a topic, idea, or rough notes. Uses Unicode bold/italic formatting that renders visually on LinkedIn.
---

Draft a LinkedIn post based on what the user has described.

## Unicode Formatting Reference

Use these Unicode character ranges to apply visual formatting (LinkedIn doesn't support markdown, but these render as styled text):

**Bold** — Mathematical Sans-Serif Bold block (𝗔–𝗭, 𝗮–𝘇, 𝟬–𝟵):
Map each letter: A→𝗔 B→𝗕 ... Z→𝗭 / a→𝗮 b→𝗯 ... z→𝘇

**Italic** — Mathematical Sans-Serif Italic block (𝘈–𝘡, 𝘢–𝘻):
Map each letter: A→𝘈 B→𝘉 ... Z→𝘡 / a→𝘢 b→𝘣 ... z→𝘻

**Bold Italic** — Mathematical Sans-Serif Bold Italic (𝘼–𝙕, 𝙖–𝙯):
Map each letter: A→𝘼 B→𝘽 ... Z→𝙕 / a→𝙖 b→𝙗 ... z→𝙯

Use bold for:
- The opening hook line (first 1–2 lines before the fold)
- Section headers or key terms
- Calls to action

Use italic for:
- Quotes or attributed ideas
- Subtle emphasis mid-paragraph

Use plain text for the body — don't over-format.

## Post Structure

Follow this structure unless the user specifies otherwise:

1. **Hook** (bold, 1–2 lines) — surprising stat, contrarian take, or direct question. This must stand alone before the "see more" fold.
2. **Story / Context** (3–6 lines plain) — the situation, problem, or experience
3. **Insight / Lesson** (2–4 lines, key phrase bolded) — the takeaway
4. **Call to action** (1 line) — ask a question or invite comments

Line breaks: use single blank lines between sections. LinkedIn wraps at ~140 chars per visual line — keep sentences short.

Hashtags: 3–5 relevant tags at the end, lowercase, e.g. #dataengineering #ai #careergrowth

## Tone

- First person, conversational, direct
- No corporate jargon, no filler phrases ("In today's fast-paced world...")
- Concrete and specific over vague and general
- Honest > polished

## Output

Output the full post ready to paste into LinkedIn. Include the Unicode-formatted characters inline — not placeholders. After the post, show a short note on what formatting choices were made and why.
