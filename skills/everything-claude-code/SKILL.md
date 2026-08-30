---
name: everything-claude-code
description: Master agent orchestration guide for Claude Code and autonomous agents. Defines specialized sub-agent hierarchies, strict tool routing, cross-platform path resolution, and context isolation protocols.
metadata:
  version: "2.0.0"
  audience: developers
---

# Everything Claude Code — Master Agent Engineering Patterns

Operate as a lead controller enforcing tool safety, context preservation, and deterministic sub-agent lifecycle management.

## 1. Tool Routing Matrix

| Intent | Primary Tool | Fallback / Alternative | Anti-Pattern | Rationale |
|---|---|---|---|---|
| Find files by pattern | `glob` | `bash (find)` | Recursive `read` | Instant native AST index; zero shell subshell cost |
| Search code/symbols | `rg` (ripgrep) | `grep` / `ast-grep` | Unfiltered file dumps | Keeps context window free of unrelated symbols; use `rg -n` for line numbers and `rg -t` for type filtering |
| Read source file | `read` (with offset/limit) | `read` (full) | Full read on >200 lines | Up to 90% token reduction per file inspection |
| Edit existing code | `edit` | Patch script | Full-file `write` | Produces clean, atomic unified diffs |
| CLI / Tests / Builds | `bash` + `rtk` | `bash` + stream pipe | Raw noisy shell exec | Truncates build spam and noisy logs by 80%+ |
| Open-ended research | `task` (sub-agent) | Manual sequential read | Context-polluting loops | Sub-agent context is isolated and purged post-run |

> **Search Tooling (`rg` over `grep`)**: ALWAYS prefer `ripgrep` (`rg`) for codebase searches. Use flags like `rg -n "pattern"` to capture line numbers for surgical edits, and `rg -t ts "pattern"` to restrict searches to specific file types. Never use generic `grep` unless `rg` is unavailable in the environment.
>
> **Installer-Assisted Tooling**: The bundle's `install.sh` installs and/or verifies `ripgrep`, `ast-grep`, `tsc` (TypeScript), `mypy`, and `pytest` when available. Prefer these tools in their domains (`ast-grep` for semantic search, `tsc`/`mypy` for type auditing, `pytest` for test validation).

---

## 2. Sub-Agent Archetypes & Delegation

When delegating via `task`, enforce specialized roles to keep sub-agents bounded:

* **Explorer Agent (Read-Only)**:
  * **Scope**: Codebase mapping, dependency tracing, finding references.
  * **Constraint**: Strictly forbidden from invoking `edit`, `write`, or mutating `bash` commands.
  * **Output Contract**: Returns a Markdown table of files, line numbers, and identified signatures.
* **Executor Agent (Implementation)**:
  * **Scope**: Surgical code edits across a single bounded module.
  * **Constraint**: Must verify syntax and run localized unit tests before completing.
* **Auditor Agent (Verification)**:
  * **Scope**: Linting, type-checking (`tsc`, `mypy`), and test suite validation.
  * **Constraint**: Only returns error traces or a green confirmation badge.

When the orchestrator needs reusable, stable roles, declare them as YAML personas instead of ad-hoc instructions. Each persona carries its scope, constraints, and output contract so delegation stays deterministic:

```yaml
explorer:
  scope: codebase-mapping | dependency-tracing | reference-finding
  read_only: true
  output_contract: markdown-table of files + line numbers + signatures
executor:
  scope: surgical-edits within one bounded module
  constraints: [verify-syntax, run-localized-tests]
  output_contract: edit summary + verification result
auditor:
  scope: lint | type-check | test-suite
  output_contract: error traces OR green confirmation badge
```

---

## 3. Sub-Agent Handoff & Synthesis Protocol

1. **Context Pruning**: The primary agent must pass only specific file paths and explicit objectives to the sub-agent.
2. **Deterministic Return**: Sub-agents must conclude with a structured synthesis block:
   ```markdown
   ### Sub-Agent Output
   - **Status**: SUCCESS | BLOCKED
   - **Files Inspected/Modified**: `path/to/file.ts:10-45`
   - **Key Finding / Action Taken**: 1-2 sentence technical summary
   ```
3. **No Context Inheritance**: Primary agent discards raw sub-agent logs and retains only the structured synthesis block.

---

## 4. Environment & Platform Governance

* **Shell Execution**: Run commands in the primary POSIX/WSL environment. Always prefix terminal calls with `rtk` where available (`rtk git status`, `rtk cargo test`, `rtk pytest`).
* **Path Resolution**:
  * Normalize paths relative to the active project root (`./src/...`).
  * For host/virtualized boundaries: map `C:\...` to `/mnt/c/...` transparently without breaking relative tool lookups.
* **Secret Zero-Tolerance**: Never print, pass as arguments, or commit API keys, auth tokens, `.env` values, or private certificates.
* **Runtime Guardrails (Hooks)**: Register `PreToolUse` hooks in `settings.json` to gate sensitive tool calls before they execute:
  * **Block** (exit 2): refuse a call that would leak a secret or mutate an unintended target.
  * **Alert** (exit 1): surface a warning and proceed after review.
  * **Auto-correct**: rewrite the input (e.g., strip a credential pattern) and continue.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [{"type": "command", "command": "rtk hook claude secret-guard"}]
      }
    ]
  }
}
```
  * Register the hook once via `rtk`; never copy a hook definition into a destination where `rtk` is not installed.

---

## 5. Artifact & Cache Lifecycle

* **Intermediate Artifacts**: Heavy AST graphs, raw JSON payloads, and CLI output captures must live in `.ai-cache/`.
* **State Synchronization**: Maintain real-time task status using `todowrite` to retain execution checkpoints without conversational overhead.
* **Persistent Memory**: Store reusable findings, decisions, and environment notes in `.ai-cache/` (or the workspace memory dir) so later sessions resume from recorded state instead of re-discovering it. Keep secrets out of memory artifacts; reference them by environment variable only.
* **Security Policies**: Sanitize secrets in all output (logs, hooks, diffs, memory). Blocklist patterns for API keys, tokens, and `.env` values; if a secret appears in a tool call or artifact, truncate it and treat the call as blocked until manually reviewed.