# AGENTS.md — ai-governance bundle

> Compact ramp-up for OpenCode/Claude sessions. Only repo-specific gotchas — trust `install.sh` and `README.md` over prose.

## What this repo is
Distribution bundle for AI agent config (Claude Code / opencode / .agents / Copilot / Gemini / Trae / Devin / Windsurf). **No build, no tests, no package manager.** Entrypoint is `install.sh` + `skills/*/SKILL.md`. Do not look for `npm test` / `cargo build`.

## Structure (real ownership)
- `skills/*/` — 15 skills, each **must** contain `SKILL.md` with frontmatter `name, description, metadata.version`. Optional `scripts/` (e.g., `graphify/scripts/graphify.py`, `security-audit-five/scripts/generate_report.py`, `smart-doc-converter/scripts/convert.py`).
- `CLAUDE.md` — only imports `@RTK.md @RULES.md @SKILLS.md` (thin router, keep it).
- `RULES.md` — governance + token-economy source of truth. Contains 12 placeholders `<USER_NAME> <PROFESSIONAL_ROLE> <PRIMARY_COMPANY> <CLIENT_NAME_A/B/C> <PERSONAL_GITHUB_USER> <WORK_GITHUB_USER> <PERSONAL_WORKSPACE> <WORK_WORKSPACE> <NON_CODE_DIR> <HOST_OS_TYPE>` — substituted only by `install.sh` interactive mode.
- `RTK.md` / `settings.json` — RTK (Rust Token Killer) wrapper. `settings.json` registers `rtk hook claude` on `PreToolUse:Bash`. **Do not copy hook if `rtk` not installed** — breaks every Bash call.
- `install.sh` — **executable source of truth** for targets, flags, and dependency fallbacks.
- `.gitattributes` forces `eol=lf` for `*.sh *.py *.md *.json` — CRLF breaks `install.sh` (`$'\r': command not found`).

## Install & verify (exact commands agents guess wrong)

```bash
# Interactive (collects 12 placeholders, installs markitdown/rg/rtk):
chmod +x install.sh && ./install.sh
# Non-interactive / CI:
./install.sh --non-interactive --force --skip-markitdown
# Windows: bash wrapper required, never PowerShell directly:
wsl bash install.sh
# Manual mirror (what install.sh does):
mkdir -p ~/.claude/skills && cp -r skills/* ~/.claude/skills/
cp CLAUDE.md RULES.md SKILLS.md RTK.md ~/.claude/

# Dependency checks (install.sh does PEP 668 fallback --break-system-packages -> pipx -> venv):
python3 -m pip install --user markitdown          # smart-doc-converter
python3 -m pip install --user "reportlab==4.2.0" "matplotlib==3.9.2"  # security-audit-five PDF only
pip install --user markitdown  # fails on Python 3.12+ without --break-system-packages -> use pipx
rg --version; rtk gain  # rtk gain must succeed, else you have Rust Type Kit (cargo uninstall rtk; cargo install --git https://github.com/rtk-ai/rtk rtk)
```

Supported `TARGET_DIRS` in `install.sh:236`: `~/.agents ~/.claude ~/.config/opencode ~/.copilot ~/.devin ~/.gemini ~/.opencode ~/.trae ~/.windsurf`. `--force` only creates `~/.claude`. `settings.json` is copied only if missing at destination.

## Skills contract (what breaks silently)
- Discovery: `~/.claude/skills/<name>/SKILL.md` (global) or `./skills/<name>/SKILL.md` (repo-local) or `~/.config/opencode/skills/`. Location documented in `SKILLS.md`.
- Adding a skill: create `skills/<kebab-name>/SKILL.md` + `scripts/` if needed, add entry `## N. \`<name>\`` to `SKILLS.md`, run `install.sh` or `cp -r` to all three roots (`C:\Users\walis\.claude\skills`, `D:\...\ai-governance\skills`, `/root/.claude/skills` via WSL).
- `smart-doc-converter:1` — must convert `pdf/docx/xlsx/ppt` via `python scripts/convert.py <file>` before reading; cached by mtime.
- `security-audit-five:1` — decoupled: `python scripts/generate_report.py --format md` always works (zero deps, writes `docs/security-audit/relatorio-auditoria-seguranca.md + findings.json`); `--format both/pdf` needs venv. Never `sys.exit(1)` on missing deps.
- `graphify:1` — `python scripts/graphify.py <path> --format summary|mermaid|json` — ignores `.git node_modules .venv .ai-cache`. Returns 0 files on this bundle (expected, no TS/JS).

## Repo-specific conventions (differ from defaults)
- **WSL-first**: `RULES.md:4` — execute all terminal commands via WSL (`rtk git status`, `rtk ls`). Host paths (`C:\...` / `D:\...`) are canonical; WSL `/home` is ephemeral.
- **Token economy**: prefer `rg -n` over `grep`, `glob` before `read`, `read` with `offset/limit`, `rtk` prefix when available. Intermediate analysis goes to `.ai-cache/` (gitignored).
- **No anemic placeholders**: `RULES.md` placeholders must stay `<UPPER_SNAKE>` until `install.sh` substitutes via `sed`. Do not commit substituted personal values upstream.
- **Never commit** `settings.local.json`, absolute host paths, or `.dsh**` (see `.gitignore`).
- **Line endings**: fix `install.sh` CRLF with `sed -i 's/\r$//' install.sh` or `dos2unix`.

## Verification (no test suite)
```bash
bash -n install.sh && echo "syntax OK"
head -n 5 skills/<name>/SKILL.md  # frontmatter present
./install.sh --help
# Dry-run install to temp HOME:
HOME=$(mktemp -d) bash install.sh --non-interactive --force --skip-markitdown --skip-rtk-check; ls $HOME/.claude/skills | wc -l
```

If docs conflict with `install.sh`, trust `install.sh`.
