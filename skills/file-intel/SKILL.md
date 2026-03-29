---
name: file-intel
description: Convert PDFs and documents in inbox/ into full markdown notes and place them in the right vault folder. The whole knowledge base stays in MD format. Use when processing imported files.
---

# File Intel — PDF to Full Markdown Note

## Step 1: Get the folder
Use `AskUserQuestion`:
```
Question: "Which folder should I process?"
Options:
1. "inbox/" — process all files in inbox/
2. "Custom path" — user specifies a folder
```

## Step 2: Ask processing mode
Use `AskUserQuestion`:
```
Question: "How should I process the files?"
Options:
1. "Parallel — process all files at once (faster)"
2. "Sequential — process one file at a time, end to end (safer, easier to follow)"
```

## Step 3: List files
Use Glob or Bash to list all supported files in the folder:
```bash
find <folder_path> -maxdepth 1 -type f \( -iname "*.pdf" -o -iname "*.pptx" -o -iname "*.xlsx" -o -iname "*.docx" -o -iname "*.csv" -o -iname "*.json" -o -iname "*.txt" -o -iname "*.md" \)
```

## Step 4: Process files

### If parallel:
Read all files simultaneously using the Read tool. For each file, extract the full content and write a complete markdown note (see format below). Do all reads in parallel, then write all notes.

### If sequential:
For each file, one at a time:
1. Tell the user: "Processing file N of M: `filename`"
2. Read the file using the Read tool
3. Extract and write the full markdown note
4. Confirm: "Done: `<destination>/<filename>.md` written"
5. Move to the next file

## Step 5: Write full markdown notes
For each file, create a proper `.md` note — NOT a summary, the **full content** as structured markdown:

```markdown
---
source: <original filename>
date-imported: YYYY-MM-DD
type: <paper | report | course-notes | reference | data>
tags: [<inferred tags>]
---

# <Title inferred from content>

## Overview
<!-- 2-3 sentence description of what this document is -->

## Key Content
<!-- Full extracted content, structured with headers -->

## Key Takeaways
<!-- Most important points -->

## Data / Tables
<!-- Any tables or structured data, converted to markdown tables -->

## Related Notes
<!-- [[wikilinks to related vault notes]] -->
```

## Step 6: Place in the right folder
Based on the content, place each `.md` file in:
- `learning/` — courses, tutorials, concept explanations
- `research/` — papers, deep dives, technical reports
- `data-engineering/` — pipeline docs, schema docs, tool references
- `resources/` — reference material, cheat sheets
- `personal/` — non-work documents

Tell the user where each file landed.

## Step 7: Clean up inbox
After all files are processed, ask: "All done — want me to delete the original files from inbox/?"

## Notes
- Supported formats: PDF, PPTX, XLSX, DOCX, CSV, JSON, XML, MD, TXT
- Full content extraction — not summaries
- Each file becomes a standalone, wikilink-ready `.md` note
