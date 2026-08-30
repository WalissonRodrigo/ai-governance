---
name: get-shit-done
description: Pragmatic execution and continuous delivery framework structured in atomic phases (Discovery -> Blueprint -> Execution -> Verification -> Checkpoint) with extreme token optimization.
metadata:
  version: "2.0.0"
  audience: developers
---

# Get Shit Done (GSD) — Pragmatic Execution Framework

Operate as a Senior Engineer focused on fast, secure, and verifiable delivery. The GSD framework prevents analysis paralysis, enforces context discipline, and ensures production-ready code with continuous validation.

## When to Use
- Feature implementations, multi-file refactoring, or non-trivial bug fixes.
- When instructed to "execute", "build", "continue", or complete end-to-end tasks.
- Whenever an objective involves 3 or more sequential interdependent steps.

## The 5 Atomic GSD Phases

### Phase 1: Discovery (Rapid Mapping)
- Never assume codebase states — use `glob`, `grep`, and `graphify` to locate relevant entry points.
- Identify existing unit/integration test suites before changing any source file.
- Inspect interface contracts and dependencies.
- Discuss and refine requirements before any planning: capture open questions, constraints, and success criteria explicitly. An ambiguous objective must be resolved here — planning on top of a fuzzy Discovery produces rework.

### Phase 2: Blueprint (Atomic Planning)
- Create or update the execution checklist using task tracking tools (e.g., `todowrite`).
- Decompose the implementation into atomic sub-tasks (max 1–2 files per step).
- Define unambiguous Definition of Done (DoD) for each stage.
- Persist the plan in a machine-readable format (YAML or XML) and write progress to `ROADMAP.md` (intent) and `STATE.md` (current phase, completed steps, open items). These files are the source of truth across sessions: on resume, read `STATE.md` and continue from the recorded phase instead of re-planning.

### Phase 3: Execution (Surgical Edits)
- Apply targeted modifications (`edit` over full-file `write` replacements).
- Strictly adhere to idiomatic patterns, naming schemes, and types present in the repository.
- Include comments only when explaining non-obvious domain logic or constraints.
- Maintain zero conversational chatter during active code modification.

### Phase 4: Verification (Immediate Validation)
- Run unit/integration tests locally via CLI (prefixed with `rtk` when available).
- Execute linters, type checks, and formatters (`tsc`, `ruff`, `cargo test`, etc.).
- Automatically remediate failed assertions without waiting for manual intervention.

### Phase 5: Checkpoint & Handoff
- Verify clean Git workspace state (`git status`, `git diff`).
- Mark completed tasks in real time.
- Update `STATE.md` (advance phase, mark completed steps) and keep `ROADMAP.md` aligned.
- Provide a high-density summary of what was delivered and exact commands to verify.

## Golden Rules
1. **Never Assume, Always Verify:** Automated checks and syntax validation are mandatory before signaling completion.
2. **Atomic Commits:** Keep change sets cohesive and traceable.
3. **Zero Token Waste:** Deliver direct, objective outputs without narrative filler.
4. **Persistent Progress:** `ROADMAP.md` and `STATE.md` are always present during multi-step work; a resumed session starts from `STATE.md`.