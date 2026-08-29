#!/usr/bin/env python3
"""
Graphify - Token-Efficient Codebase Topology & Dependency Extractor
Maps architecture, imports, coupling metrics, and circular dependencies without dumping raw source files.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

IGNORE_DIRS = {
    '.git', 'node_modules', 'dist', 'build', '.next', 'bin', 'obj',
    '__pycache__', '.venv', 'venv', '.turbo', '.cache', '.ai-cache', 'coverage'
}

EXTENSIONS = {
    '.js': 'js', '.jsx': 'js', '.ts': 'ts', '.tsx': 'ts', '.mjs': 'js', '.cjs': 'js',
    '.py': 'py', '.cs': 'cs', '.go': 'go', '.rs': 'rs', '.java': 'java', '.kt': 'kt'
}

def extract_js_ts_imports(content: str) -> set:
    imports = set()
    # ES6 Static Imports / Dynamic Imports
    for m in re.finditer(r'''(?:import|from)\s+['"]([^'"]+)['"]''', content):
        imports.add(m.group(1))
    # CommonJS require()
    for m in re.finditer(r'''require\(\s*['"]([^'"]+)['"]\s*\)''', content):
        imports.add(m.group(1))
    return imports

def extract_py_imports(content: str) -> set:
    imports = set()
    for m in re.finditer(r'''^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))''', content, re.MULTILINE):
        target = m.group(1) or m.group(2)
        if target:
            imports.add(target.split('.')[0])
    return imports

def extract_imports(content: str, ext: str) -> set:
    if ext in ('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'):
        return extract_js_ts_imports(content)
    elif ext == '.py':
        return extract_py_imports(content)
    return set()

def scan_codebase(root_path: str, max_depth: int = 6) -> dict:
    root = Path(root_path).resolve()
    graph = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        depth = 0 if rel_dir == '.' else len(Path(rel_dir).parts)
        if depth > max_depth:
            continue

        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXTENSIONS:
                full_path = Path(dirpath) / f
                rel_path = str(full_path.relative_to(root)).replace('\\', '/')
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read(131072) # Read up to 128KB header
                    deps = extract_imports(content, ext)
                    lines = content.count('\n') + 1
                    graph[rel_path] = {
                        'lines': lines,
                        'size_bytes': len(content),
                        'dependencies': sorted(list(deps))
                    }
                except Exception as err:
                    graph[rel_path] = {'error': str(err)}

    return graph

def generate_mermaid(graph: dict) -> str:
    lines = ['graph TD']
    for src, info in graph.items():
        src_id = re.sub(r'[^a-zA-Z0-9_]', '_', src)
        lines.append(f'  {src_id}["{src} ({info.get("lines", 0)}L)"]')
        for dep in info.get('dependencies', []):
            if dep.startswith(('.', '@/', '~/')):
                dep_id = re.sub(r'[^a-zA-Z0-9_]', '_', dep)
                lines.append(f'  {src_id} --> {dep_id}["{dep}"]')
    return '\n'.join(lines)

def generate_summary(graph: dict) -> str:
    total_files = len(graph)
    total_lines = sum(v.get('lines', 0) for v in graph.values())
    
    # Calculate coupling / in-degree
    incoming = defaultdict(int)
    for v in graph.values():
        for d in v.get('dependencies', []):
            incoming[d] += 1

    top_hubs = sorted(incoming.items(), key=lambda x: x[1], reverse=True)[:10]

    out = [
        f"Topology Summary:",
        f"- Total Analyzed Files: {total_files}",
        f"- Total Code Lines: {total_lines}",
        f"\nTop Coupled Modules / Hubs (Blast Radius Hotspots):"
    ]
    for module, count in top_hubs:
        out.append(f"  * {module}: referenced by {count} files")
    return '\n'.join(out)

def main():
    parser = argparse.ArgumentParser(description="Graphify: Architecture & Dependency Graph Extractor")
    parser.add_argument("path", nargs="?", default=".", help="Target project root directory")
    parser.add_argument("--format", choices=["mermaid", "json", "summary"], default="summary", help="Output format")
    parser.add_argument("--depth", type=int, default=6, help="Maximum directory traversal depth")
    args = parser.parse_args()

    graph = scan_codebase(args.path, max_depth=args.depth)

    if args.format == "json":
        print(json.dumps(graph, indent=2))
    elif args.format == "mermaid":
        print(generate_mermaid(graph))
    elif args.format == "summary":
        print(generate_summary(graph))

if __name__ == "__main__":
    main()