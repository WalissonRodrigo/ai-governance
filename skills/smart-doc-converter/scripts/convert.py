#!/usr/bin/env python3
"""Universal document to Markdown converter (smart-doc-converter)."""

import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Convert Office and PDF documents to Markdown.")
    parser.add_argument("source", help="Path to source document (.pdf, .docx, .xlsx, .pptx, etc.)")
    parser.add_argument("output", nargs="?", default=None, help="Optional output Markdown file path")
    parser.add_argument("--force", action="store_true", help="Force reconversion even if cache is valid")
    
    args = parser.parse_args()
    
    src = Path(args.source).resolve()
    if not src.exists():
        print(f"Error: Source file not found at '{src}'.", file=sys.stderr)
        sys.exit(1)
        
    dest = Path(args.output).resolve() if args.output else src.with_name(f"{src.name}.md")
    
    # Smart cache bypass check
    if not args.force and dest.exists():
        if dest.stat().st_mtime > src.stat().st_mtime:
            print(f"Cache hit: using existing converted file at '{dest}'.")
            return

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("Error: 'markitdown' is not installed. Run 'pip install markitdown'.", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Converting '{src.name}' to Markdown...")
        result = MarkItDown().convert(str(src))

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(result.text_content, encoding="utf-8")

        print(f"Success: output generated at '{dest}'.")
    except Exception as e:
        print(f"Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()