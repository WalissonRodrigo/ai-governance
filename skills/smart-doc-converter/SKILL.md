---
name: smart-doc-converter
description: Universal document converter (PDF, Word, Excel, PowerPoint) to Markdown. Intercepts binary files before reading to optimize token consumption and preserve tabular data.
metadata:
  version: "2.1.0"
  audience: developers
---

# Smart Doc Converter

Operate under a strict token-conservation protocol. **Never read raw binary documents directly** (`.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`). Always convert them to Markdown first.

## Trigger Conditions
Automatically trigger this workflow whenever a file with any of the following extensions is referenced, attached, or requested:
- PDF: `.pdf`
- Word: `.docx`, `.doc`
- Excel: `.xlsx`, `.xls`
- PowerPoint: `.pptx`, `.ppt`

## Execution Protocol

### Step 1: Run Conversion
Execute the bundled Python script to convert the document into Markdown:

python <SKILL_DIR>/scripts/convert.py "<path/to/document.pdf>"

Options:
- Default output: Creates `<source-path>.md` alongside original file.
- Custom output: `python <SKILL_DIR>/scripts/convert.py "<path/to/document.pdf>" ".ai-cache/document.md"`
- Force conversion: `python <SKILL_DIR>/scripts/convert.py "<path/to/document.pdf>" --force`

Note: `<SKILL_DIR>` resolves to the directory where this `SKILL.md` is installed.

### Step 2: Ingest the Markdown File
- Inspect the generated `.md` file using standard reading tools (`read` / `grep`).
- Treat the generated Markdown as the single source of truth for text, tables, and document layout.

### Step 3: Respond to User
- Provide answers, data extraction, or summaries based solely on the generated Markdown.
- Keep internal conversion mechanics silent unless the user explicitly asks.

## Caching Behavior
- The script checks modification times (`mtime`).
- If the output `.md` already exists and is newer than the source document, conversion is skipped.
- Use `--force` to bypass cache when needed.