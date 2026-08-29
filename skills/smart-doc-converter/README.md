# smart-doc-converter

Agent skill that intercepts binary documents (PDF, Word, Excel, PowerPoint) and converts them into structured Markdown **before** ingestion by an AI model.

## Features
- **Token Efficiency**: Drastically cuts down token usage compared to raw binary or OCR parsing.
- **Tabular Preservation**: Accurately formats Excel tables and Word documents into GitHub-flavored Markdown.
- **Smart MTime Cache**: Skips redundant processing when files haven't changed.

## Requirements
- Python 3.9+
- `markitdown` (`pip install markitdown`)

## Installation Paths

| Tool | Global Path | Project Path |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/smart-doc-converter/` | `.claude/skills/smart-doc-converter/` |
| OpenCode | `~/.config/opencode/skills/smart-doc-converter/` | `.opencode/skills/smart-doc-converter/` |
| Agent Frameworks | `~/.agents/skills/smart-doc-converter/` | `.agents/skills/smart-doc-converter/` |

## Manual CLI Usage
```bash
python scripts/convert.py document.pdf
python scripts/convert.py document.pdf .ai-cache/doc.md
python scripts/convert.py document.pdf --force