---
name: refresh
description: Re-verify a note against its canonical source URL, diff against current claims, propose updates, and bump last_verified. Usage - /refresh <note-path> or /refresh (prompts for note). Closes the staleness loop without deleting the original.
---

# Refresh — Re-verify a Note Against Its Source

Vault root: `{{VAULT}}/`

## Step 1: Identify the note

If the argument is a file path, read that note.
If no argument, ask: "Which note do you want to re-verify? (e.g. `learning/langgraph/state-and-reducers`)"

Read the note fully and extract:
- `source:` URL from frontmatter
- `last_verified:` date
- `verified_against_version:` if present
- All factual claims (bullet points, code snippets, key assertions)

If `source:` is missing or is `"training-data"`, ask: "What's the canonical URL for this note?" and add it to frontmatter before continuing.

---

## Step 2: Fetch current source

Use the `defuddle` skill to fetch and clean the `source:` URL into markdown.

If the URL is broken or times out, report: "Source URL unreachable — cannot re-verify. Update `source:` in frontmatter and retry."

---

## Step 3: Diff current claims against source

Read both the note and the fetched source. Compare:
1. **Still accurate** — claims that match current source content
2. **Outdated** — claims in the note that contradict or are absent from the current source (version changes, deprecated APIs, changed behavior)
3. **New in source** — important content in the current source not yet in the note
4. **Version bump** — if the source mentions a new library version that's different from `verified_against_version`

Present the diff as:

```
## Refresh diff: [[learning/langgraph/state-and-reducers]]
Source: https://... (fetched YYYY-MM-DD)

### ✅ Still accurate (N claims)
- ...

### ⚠️ Outdated (N claims)
| Claim in note | Current source says |
|---|---|
| "use add_messages reducer" | Now: use MessagesState directly (v1.0+) |

### 🆕 New in source (N items worth adding)
- ...

### 📦 Version: note says X, source says Y
```

---

## Step 4: Propose changes

Ask: "Apply these updates?"

If yes:
1. Edit the note to fix outdated claims (preserve existing structure; don't rewrite clean sections)
2. Add new content under the appropriate heading
3. Update frontmatter:
   ```yaml
   last_verified: <TODAY>
   confidence: high           # bump to high after re-verification
   verified_against_version: "<new version if changed>"
   ```
4. If provenance of updated claims is now `extracted`, update to `extracted`

---

## Step 5: Log

Append to `wiki/log.md`:
```
## [DATE] refresh | <Note title>
- Note: [[folder/slug]]
- Source: <url>
- Changes: N outdated fixed, N new added, version bumped to X
- last_verified: <TODAY>
```
