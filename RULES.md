# SYSTEM & AGENT GOVERNANCE RULES

## 1. Execution Context & Tooling
- **Environment**: ALWAYS execute terminal commands via WSL (Linux/Ubuntu). Never execute direct commands on native Windows/PowerShell unless explicitly instructed.
- **CLI Compression Wrapper (RTK)**: ALWAYS prefix shell/CLI commands with `rtk` (Rust Token Killer) to compress tool outputs and conserve context window (e.g., `rtk git status`, `rtk cargo test`, `rtk ls src/`, `rtk grep`).
- **Web Access & Retrieval**: 
  - ALWAYS prioritize lightweight MCPs or CLI tools (`rtk curl`, direct API/HTTP fetch) to retrieve web data as raw text or JSON.
  - Avoid launching headless browser environments (Puppeteer/Playwright/Browser Bridge) unless interacting with complex JS-rendered pages is strictly mandatory.

---

## 2. Profile & Stakeholder Context

<!-- 
CONFIGURATION / PLACEHOLDER GUIDE:
Customize the following template variables to match your personal profile and client roster:
- <USER_NAME>             : Your name or preferred identifier
- <PROFESSIONAL_ROLE>     : Your primary title/role (e.g., Staff Engineer, Solutions Architect)
- <PRIMARY_COMPANY>       : Your agency, company, or consulting business name
- <CLIENT_NAME_A, B, C>   : List of active clients, enterprise accounts, or affiliated groups
-->

- **User Profile**: `<USER_NAME>` — `<PROFESSIONAL_ROLE>`.
- **Clients & Associated Entities**: `<CLIENT_NAME_A>`, `<CLIENT_NAME_B>`, `<CLIENT_NAME_C>` (clients/partners of `<PRIMARY_COMPANY>`).
- **Strict Client Confidentiality & Isolation**: Never mention or cross-reference any client or entity without explicit project context. Regardless of whether tasks involve ongoing, future, or legacy client scopes, maintain strict zero-leakage boundaries: when in doubt, omit client names entirely. No client-facing artifact or communication may contain references, identifiers, or proprietary context belonging to another entity.


### Git/GitHub Identity per Workspace

<!-- 
CONFIGURATION / PLACEHOLDER GUIDE:
Customize the following template variables to match your environment:
- <PERSONAL_GITHUB_USER> : Your personal/open-source GitHub username (default)
- <WORK_GITHUB_USER>     : Your work/client/organization GitHub username
- <PERSONAL_WORKSPACE>   : Path to your personal coding workspace (e.g., C:\Users\<user>\Projects\Personal)
- <WORK_WORKSPACE>       : Path to your company/client coding workspace (e.g., C:\Users\<user>\Projects\Work)
- <NON_CODE_DIR>         : (Optional) Folder holding non-code files/docs that should be ignored for dev tasks
- <HOST_OS_TYPE>         : Host OS indicator (e.g., Windows/macOS/Linux) vs virtualized env (e.g., WSL/Containers)
-->

- **`<PERSONAL_GITHUB_USER>`** (Personal Account): **DEFAULT** identity for all non-work tasks (issues, PRs, forks, commits, and general GitHub operations). Always use within the **`<PERSONAL_WORKSPACE>`** directory and for any personal or open-source projects.
- **`<WORK_GITHUB_USER>`** (Work Account): **EXCLUSIVE** identity for tasks inside the **`<WORK_WORKSPACE>`** directory. Never use outside of this specific workspace context.
- **Workspace Location & Path Conventions**: The active workspace is located on the host filesystem at `<PERSONAL_WORKSPACE>`. Always operate within the host filesystem paths (e.g., Windows side) rather than internal virtualized environments (e.g., WSL `/home/...`). Abstract the host/virtualized boundary by resolving paths and executing tooling directly against the host workspace.
- **Non-Code Directories**: `<NON_CODE_DIR>` is NOT a development workspace (it contains only administrative, legal, or fiscal documents). Do not use this directory for coding or repository tasks.
- **Strict Account Isolation**: Never mix accounts across workspaces. If the required account credentials are not active in the current environment, prompt for user confirmation before executing any `git` or `gh` commands.
- **Multi-Account CLI Management**: Both accounts remain authenticated simultaneously in the GitHub CLI (`gh`). Before running Git/GitHub commands, select the correct active identity for the current workspace context:
  ```bash
  # Authenticate an account (one-time setup)
  gh auth login --hostname github.com --web

  # Switch to target workspace identity (<PERSONAL_GITHUB_USER> or <WORK_GITHUB_USER>)
  gh auth switch --user <GITHUB_USER>

  # Confirm active identity
  gh auth status

```


---

## 3. Architecture & Engineering Standards

### Core Paradigms & Design Principles
- **SOLID, DRY, KISS, YAGNI**:
  - Keep components modular, single-responsibility, and strictly typed.
  - Avoid over-engineering: do not introduce abstractions, design patterns, or extra layers until explicitly required by current specs (YAGNI/KISS).
  - Do not duplicate logic, types, or constants across files (DRY).
- **Domain-Driven Design (DDD)**:
  - Isolate Core Domain logic inside pure Domain entities and value objects with zero framework or external infrastructure dependencies.
  - Preserve ubiquitous language naming consistently across code, domain models, tests, and documentation.
- **Clean Architecture & OOP**:
  - Enforce clear dependency boundaries: Domain -> Application (Use Cases) -> Infrastructure/Adapters.
  - Rely on dependency inversion (interfaces/traits/abstract contracts) at boundary limits.
  - Model business rules using rich OOP Domain Models; strictly avoid anemic domain models.
- **Test-Driven Development (TDD)**:
  - Write or update failing unit/integration tests before implementing code features or bug fixes.
  - Run local validation tests via WSL before signaling task completion.

---

## 4. Token Economy & High-Scale Audit Strategies

- **Static Analysis First**: NEVER dump whole codebase files into the context window when auditing, mapping, or understanding system structures. ALWAYS generate or inspect structural outlines first (AST, export signatures, package manifests).
- **Targeted Grep/Search**: Before asking the model to read a file, use precise search filters (`rtk grep`, `rtk find`, `ripgrep`) to isolate relevant modules (e.g., Auth, Identity, Tokens, Handlers).
- **Incremental Caching**: When conducting multi-repo or large-scale technical analysis (e.g., IAM architectures), store intermediate findings in a local `.ai-cache/` directory. Refer to cached `.md` summaries instead of re-reading raw repositories.
- **Pre-Filtering Scripting**: Favor lightweight local WSL shell scripts (`find`, `awk`, `jq`, `ast-grep`) to compile data/JSON reports before consuming context window tokens.
- **Compact Output Constraints**: Always format findings in high-density, concise Markdown tables or condensed YAML — avoid conversational fluff, self-reflections, and redundant boilerplate.

---

## 5. Operations & Safety Rules

- **Read-Only Mode**: During technical analysis, mapping, or reverse engineering, DO NOT edit code, run mutating commands, or commit changes without explicit instruction.
- **Source of Truth**: Reverse-engineer actual source code as the primary truth for logic. Use local `.md` files as the single source of truth for external docs/publications.
- **Proposal Validation**: Before modifying original documentation or core architecture, propose changes in a `.proposta-revisada.md` file first.
- **Environment Bootstrapping**: Always maintain `setup.sh` and `WORKSPACE-README.md` to ensure identical local workspace replication.
- **Workspace Cleanup**: Redundant, temporary, or orphan files may be cleaned up proactively to keep workspaces lightweight. If you need create files to execute some action, prefer use a `.ai-cache` folder to mantain cleaned structure files and folder at project/context.
- **Documentation Structure**: Separate factual code analysis from strategic governance using numbered directories (e.g., `01-analysis/`, `02-architecture/`).

---

## 6. Communication & Documentation Style

- **Ubiquitous Language & Context Mirroring**: 
  - **Dynamic Adaptation**: Analyze the codebase's existing language (variable names, domain entities, comments). If the domain is established in Brazilian Portuguese (e.g., banking systems, enterprise legacy), write all documentation, PRs, and comments in **Professional Brazilian Portuguese (pt-BR)**. For international or English-first codebases, use **100% English**.
  - **Natural Corporate Tone**: When writing in pt-BR, use native corporate terminology. Avoid literal translations of English frameworks (e.g., use "Cenário Atual / Cenário Futuro" instead of literal translations of "AS-IS / TO-BE"). Blend standard English technical terms (e.g., "deploy", "thread", "endpoint") naturally without translating them.
- **Communication Directives**: Concise, objective, and high-density ("less is more"). ZERO meta-commentary, self-reflections, or internal LLM reasoning explanations in final documents.
- **Code Traceability**: Always link technical findings or architectural proposals to specific relative file paths and line numbers (e.g., `src/domain/entities/conta-corrente.ts:42`).
- **Diagrams**: Use Mermaid diagrams for inline architectural visualization and Draw.io for complex diagrams with correct extension `.drawio` and without errors.
- **Paths**: ALWAYS use relative repository paths (`./src/...`). Never output local absolute paths.

---

## 7. Constraints & Autonomy Boundaries

- **No Architectural Assumptions**: Do not modify architecture, folder hierarchies, or create new documentation frameworks without explicit user authorization.
- **Context Isolation**: Keep technical domain details strictly isolated when generating non-technical stakeholder communications.

## 8. Read MDs before reading binaries directly
- Always use the smart-doc-converter skill for any Office file or PDF. Don't ask me before converting.
- The skill is installed in the standard skills directory (~/.claude/skills/smart-doc-converter/); its scripts/convert.py converts files [".pdf", ".xlsx", ".xls", ".docx", ".doc", ".pptx", ".ppt"] to markdown

---

## 9. Global Skills Governance & Token Optimization

<!-- 
CONFIGURATION / PLACEHOLDER GUIDE:
Customize the list below to match your installed toolset, custom skills, and execution conventions:
- <SKILLS_DIR>   : Base path where your local skills/scripts are located
- <SHELL_WRAPPER>: Command runner/wrapper used for host execution (e.g., RTK, bash, zsh)
-->

Every enabled skill serves a strict purpose: engineering rigor, architectural governance, and aggressive token optimization.

1. **`smart-doc-converter`**: IMMEDIATELY intercept `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.doc`, `.xls`, and `.ppt` files. Convert them to Markdown via `python <SKILLS_DIR>/smart-doc-converter/scripts/convert.py` before inspecting or ingesting contents into context.
2. **`graphify`**: Mandatory for mapping project topology, dependency graphs, entry points, and blast radiuses prior to any multi-file refactoring or feature work. Prevents context bloat from bulk-reading files.
3. **`cave-man`**: Apply a high-density, concise technical communication protocol across all interactions. Deliver direct, objective outputs without conversational filler, meta-announcements, redundant greetings, or repetitive preambles. Maximize signal-to-token ratio.
4. **`get-shit-done` (GSD)**: Structure non-trivial implementation workflows into atomic phases (`Discovery` -> `Blueprint` -> `Execution` -> `Verification` -> `Checkpoint`). Track progress in real time via atomic task/todo tooling to maintain execution state without context drift.
5. **`everything-claude-code`**: Adhere to core tool-use governance:
   - Prefer indexed search (`Glob`/`Grep`) before reading full files.
   - Delegate heavy parallel workloads to sub-agents.
   - Run system executions via `<SHELL_WRAPPER>`.
   - Maintain strict Git/GitHub CLI account and branch discipline.
6. **`ui-ux-pro-max` & `awesome-design-md`**: For all UI/frontend tasks, enforce semantic design tokens, WCAG AA contrast compliance, complete component interaction states (hover, focus, disabled, loading, active), and standardized `DESIGN.md` documentation.
7. **`openspec-*`**: Follow the formal feature change lifecycle (`propose`, `explore`, `apply`, `update`, `sync`, `archive`) for end-to-end architectural governance.
