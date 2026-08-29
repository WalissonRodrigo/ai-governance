---
name: graphify
description: Codebase dependency graph extraction, architectural topology mapping, and blast-radius analysis with minimal token footprint.
metadata:
  version: "2.0.0"
  audience: developers
---

# Graphify — Codebase Topology & Dependency Graph

Operate as a Software Architect focused on structural analysis and token economy. Avoid reading dozens of full files into the context window. Use `graphify` to extract relationships, entry points, and blast radiuses before modifying code.

## When to Use
- Exploring unfamiliar repositories or workspaces.
- Planning multi-file refactoring or API contract modifications.
- Calculating blast radiuses prior to architectural changes.
- Generating visual architecture diagrams (`mermaid` / `graph TD`).

## Operational Capabilities

### 1. Structural Dependency Mapping
- **Input:** Root directory or selected module path.
- **Output:** Condensed Mermaid graph or structured JSON containing:
  - System entry points.
  - Import/Export dependency edges (`A -> B`).
  - High-coupling nodes (critical hub components).

### 2. Local Script Execution
Execute the bundled Python extractor to inspect dependencies without dumping source files into context:
```bash
python <SKILLS_DIR>/graphify/scripts/graphify.py "<project-path>" [--format mermaid|json|summary] [--depth N]
```


### 3. Manual Tool-Use Fallback (Zero Token Waste)
When running natively via built-in tools (`glob`, `grep`):
1. Index the workspace tree using `glob`.
2. Extract module signatures using `grep` (filter `import`, `export`, `require`, `using`).
3. Synthesize findings into a concise Mermaid diagram:
   ```mermaid
   graph TD
     Client[lib/client.js] --> Host[lib/host.js]
     Host --> Bridge[vscode-ext/dsh-bridge/extension.js]
   ```
4. Read only the 2–3 files strictly necessary for the active task.