---
name: security-audit-five
description: Stack-aware 5-vector security audit (tenant isolation, frontend RBAC, IDOR, hardcoded secrets, XSS) — evidence-only, full route coverage, strengths proof. Decoupled reporting: Markdown always (zero deps), PDF optional (isolated venv) + GitHub-ready issues.
metadata:
  version: "1.1.0"
  audience: developers
---

# Security Audit Five — Stack-Aware 5-Vector Audit (Hybrid Decoupled)

Evidence-only. Zero speculation. Every finding: `file:line` + snippet + exploitability + severity. Enumerate audited files line-by-line; also report verified strengths to prove coverage. **Reporting is decoupled**: Markdown is the primary deliverable (works everywhere); PDF is an optional enhancement when Python is available.

## When to Use
- Pre-release security review, pentest prep, due diligence.
- User says "audit security", "5 flaws", "RLS/tenant", "IDOR", "secrets", "XSS".
- Any request mapping to the 5 vectors below.

## Execution Modes — Decoupled Design (MANDATORY)

| Mode | Deliverable | Deps | When |
|---|---|---|---|
| **A — Markdown Primary (ALWAYS)** | `docs/security-audit/relatorio-auditoria-seguranca.md` + `docs/security-audit/findings.json` | None | Every run. Works in TRAE/Cursor/Windsurf/VSCode/DSH/Claude Code, offline, read-only FS fallback to `findings.json` only. |
| **B — PDF Optional (OPT-IN)** | `docs/security-audit/relatorio-auditoria-seguranca.pdf` (A4, palette chips, charts) | `python3` + `reportlab==4.2.0` + `matplotlib==3.9.2` in isolated `.venv` | Only if `python3 --version` succeeds AND user/env allows venv. Never block Mode A. |

Rule: **Never fail the audit if PDF deps are missing**. Emit Mode A, warn, and print the one-liner to generate PDF later (see Technical Rules). Do not `sys.exit(1)` on missing deps.

## Phase 0 — Stack Fingerprint (MANDATORY FIRST)

Detect before auditing. Adapt each vector. Output a table; reuse its terminology.

| Dimension | Detect How | Examples |
|---|---|---|
| Language | `glob` manifests | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml` |
| Framework | deps + entry points | Next.js/NestJS/Express/Django/FastAPI/Spring/Gin/Rails/Laravel |
| ORM / Query | deps + `grep` imports | Prisma/Drizzle/TypeORM/Sequelize/SQLAlchemy/Eloquent/GORM |
| Auth | middleware + config | NextAuth/Auth.js/Supabase Auth/Clerk/Firebase/JWT/Passport/Devise |
| Frontend | `src/` + framework | React/Vue/Svelte/Angular/Next/SSR/none |
| Isolation | RLS/middleware/manual filter | Supabase RLS / `tenant_id` middleware / `user_id` WHERE |
| Deploy | repo root | `Dockerfile`, `docker-compose.*`, `.github/workflows`, `helm/`, `*.tf` |

1. `glob` manifests + `grep` for `supabase|prisma|drizzle|typeorm|sequelize|auth|clerk|firebase`.
2. Read 2-3 entry files (router, middleware, `supabase/migrations`).
3. Decide isolation: **RLS vs middleware vs manual `where:{userId}`**. If none, `ABSENT`.
4. If category maps poorly (no frontend → skip vector 5 frontend part, state explicitly).

> Do not start vectors until Phase 0 table is complete.

## The 5 Vectors (Stack-Adapted)

### 1 — DATABASE WITHOUT LOCK (Tenant/Owner Isolation)
Goal: every list/search/aggregation/report/export filters by authenticated user/org/tenant.
- **Supabase**: `ENABLE ROW LEVEL SECURITY` + policies `FOR SELECT/INSERT/UPDATE/DELETE USING (auth.uid() = user_id)`. Check `supabase/migrations/*.sql`.
- **API-owned DB**: Every `findMany/findWhere/select/aggregate` must include `where:{tenantId|userId|orgId|workspaceId}` from `req.user`/`ctx.auth`. Grep: `findMany|findAll|find\(|select\(|aggregate|createQueryBuilder`.
- Flag if replay with own token + forced `orgId` leaks cross-tenant.

### 2 — BROWSER-DEFINED PERMISSION (Frontend-only RBAC)
Goal: no privileged op relies solely on UI gating.
- Inventory frontend gates: `isAdmin|canEdit|role===|useRole|hasPermission|<AdminOnly|v-if="admin"` via `rg -n`.
- For each gate, locate backend handler. Backend MUST check `req.user.role`/`hasRole('admin')` before write/admin.
- Flag: `POST /admin/*`, `PUT /settings`, `DELETE /users/*` reachable with non-admin token.

### 3 — IDOR (Object-Level Authorization)
Goal: every `/:id`, `?id=`, `body.id` fetch/mutate/delete verifies ownership.
- **Enumerate ALL handlers**: `rg -n "router\.|app\.(get|post|put|patch|delete)|@Get|@Post|defineRoute"`. No sampling.
- Check: `if (obj.userId !== req.user.id && obj.orgId !== req.user.orgId) throw 403`. Joins count.
- Also batch (`/bulk`, `ids: []`) and indirect refs (slug/uuid/seq int).

### 4 — HARDCODED SECRETS (Exposed Keys)
Scan: source + `docker-compose.yml` + `Dockerfile` + `helm/values*.yaml` + `.github/workflows/*` + `*.tf` + `scripts/*` + `docs/*`.
- Patterns: `api[_-]?key|secret|password|private[_-]?key|jwt.*secret|webhook.*secret|BEGIN PRIVATE KEY`.
- Special: `${VAR:-defaultValue}` / `|| 'default'` where default is real credential. Require `if (!process.env.SECRET) throw`.
- Frontend bundle: `rg -n "NEXT_PUBLIC_|VITE_|REACT_APP_"` — any secret in client code.
- Git history: `git log --all -p -S "secret|password|key" --source` + `gitleaks`/`trufflehog` if available.
- Severity `critical` if prod-used; `high` if known default.

### 5 — UNSANITIZED INPUTS (XSS)
- **Frontend**: `innerHTML|dangerouslySetInnerHTML|v-html|[innerHTML]|bypassSecurityTrustHtml|eval\(|new Function\(|javascript:` + markdown render without sanitizer. Check `DOMPurify|sanitize-html|marked` applied per sink.
- **Backend**: user input into `sendMail({html:` / template literals / `res.send(` without `escape|sanitize`.
- Flag stored vs reflected vs DOM.

## Audit Rules (Non-Negotiable)

1. **Evidence-only**: `file:line` + snippet + why exploitable + severity `critical|high|medium|low|info`. No hypothetical.
2. **File-by-file, line-by-line**.
3. **Strengths mandatory**: e.g., "router `orders.ts:12-80` validates ownership on all 6 handlers".
4. **Category N/A**: state explicitly.
5. **Exploitability note** per finding.
6. **Severity palette**: `critical #B91C1C | high #EA580C | medium #D97706 | low #2563EB | strength #059669 | info #6B7280`.
7. **Deduplicate trivial related** into one GitHub issue.

## Workflow — 7 Phases (Decoupled)

| # | Phase | Actions | Output |
|---|---|---|---|
| 0 | Fingerprint | Stack table + isolation mechanism | Scope + methodology note |
| 1 | Tenant Isolation | RLS/policy or per-query filter audit | Findings + strengths |
| 2 | RBAC | Frontend gate ↔ backend cross | Findings + strengths |
| 3 | IDOR | Enumerate ALL route handlers | Coverage table |
| 4 | Secrets | Code+config+compose+CI+Helm+TF+git+bundle | Findings |
| 5 | XSS | Sink inventory + sanitizer verification | Findings |
| 6 | Synthesis | Dedupe, severity sort, P1/P2/P3 | `findings.json` + chat report |
| 7 | Report | **Mode A always**: `relatorio...md` + `findings.json`. **Mode B opt-in**: `relatorio...pdf` via `scripts/generate_report.py` if deps available. Copy generator to `docs/security-audit/` for later regeneration. |

Tooling: `rg -n` > `grep`; `ast-grep` for sinks; `glob` for manifests; `read` offset/limit for evidence. Never dump full files.

## Evidence Contract (per finding)

```
[SEVERITY] file:line — Category
Code: `exact snippet (1-3 lines)`
Why exploitable: one sentence
Exploitability: requires Z config? authenticated?
```

Sort `critical → info` inside each vector.

## Report Specification (MD primary, PDF mirrors it)

Language `pt-BR`. Both MD and PDF share sections `a–f`; MD is source of truth when PDF unavailable.

- **a) Capa**: title `Relatório de Auditoria de Segurança — <project>`, date `DD/MM/YYYY`, scope, methodology note = Phase 0 mapping paragraph.
- **b) Resumo executivo**: totals per severity (chips palette), donut by severity + bar by category. In MD: ASCII tables + mermaid placeholders; in PDF: `matplotlib` images.
- **c) Pontos fortes / fracos**: strengths with evidence vs central risks.
- **d) Achados detalhados por categoria**: table per vector `Severidade | Arquivo:linha | Descrição` (snippet + exploitability collapsed in MD code fences).
- **e) Recomendações priorizadas**: `P1` (critical/high, trivial exploit), `P2` (medium), `P3` (low). Each: action + file hint + effort.
- **f) ISSUES PARA O GITHUB**: one delimited block per finding/group:
  ```
  --- ISSUE n ---
  Title: [Segurança] <short>
  Labels: security, severity:critical|high|medium|low
  Body (Markdown ready):
  ## Descrição
  ## Evidência — arquivo:linha
  ```code```
  ## Por que é explorável
  ## Impacto
  ## Sugestão de correção
  ## Critérios de aceite (checklist)
  --- FIM ISSUE n ---
  ```
  Group trivial related (e.g., 5× `:-default`) into one.

## Technical Generation Rules (Decoupled, Non-Blocking)

- **Detection before execution**:
  ```bash
  if command -v python3 >/dev/null 2>&1 && python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)"; then
    echo "PDF opt-in available"
  else
    echo "PDF skipped — Mode A (MD) only"
  fi
  ```
- **Never global install**. If PDF opted-in, isolated venv only:
  ```bash
  python3 -m venv docs/security-audit/.venv
  source docs/security-audit/.venv/bin/activate  # Windows: .venv\Scripts\activate
  pip install "reportlab==4.2.0" "matplotlib==3.9.2"
  python docs/security-audit/generate_report.py --project "my-app" --findings docs/security-audit/findings.json --format both
  # fallback: --format md always works, --format pdf requires deps, --format both tries pdf then md
  ```
  If venv fails (offline/PEP 668/read-only), emit MD and print: `pip install --user ...` alternative in comment — do not abort audit.
- **Pin versions** to avoid supply-chain drift; do not `pip install reportlab matplotlib` unpinned.
- **Leave generator** at `docs/security-audit/generate_report.py` (copied from `skills/security-audit-five/scripts/generate_report.py`) for later `both` regeneration.
- **Verification** (only if PDF generated):
  ```bash
  python -c "from PyPDF2 import PdfReader; print(len(PdfReader('docs/security-audit/relatorio-auditoria-seguranca.pdf').pages))"
  ```
  If charts clipped/tables overflow, fix (font 7-8pt, wrap, paginate) and regenerate before delivery. If no PDF, verify `relatorio...md` renders in viewer.
- **Stack-local alternative**: if `package.json` present and `python3` missing, offer `npx --yes md-to-pdf` or `pandoc` as HTML→PDF path — agent picks runtime of the project, not forced Python.

## Strengths Template

```
✅ Vector 2 — Verified: middleware `src/middleware/rbac.ts:14` enforces role on all 8 admin routes; gates at `src/components/AdminPanel.tsx:22` are redundant only.
```

## When Category N/A — State It

```
Vector 5 (frontend XSS): N/A — API-only (no bundle). Backend email template XSS still audited: `src/mailer/*:18` escapes via `escapeHtml()`.
```

## Deliverables Checklist (agent MUST return)

- [ ] `docs/security-audit/findings.json` — structured findings (always)
- [ ] `docs/security-audit/relatorio-auditoria-seguranca.md` — primary report (always, zero deps)
- [ ] `docs/security-audit/generate_report.py` — copied generator (always, for later PDF)
- [ ] `docs/security-audit/relatorio-auditoria-seguranca.pdf` — **only if** Mode B succeeded (verified pages); else note `PDF skipped — run with python3 to regenerate`
- [ ] Chat findings: file-by-file, line-by-line + strengths + paths of all generated files

## Invocation Example

```bash
# Mode A always — no deps, works in any IDE/sandbox
# Agent writes findings.json + relatorio.md + copies generate_report.py
cat docs/security-audit/findings.json

# Mode B opt-in — when python3 available
python3 -m venv docs/security-audit/.venv
source docs/security-audit/.venv/bin/activate
pip install "reportlab==4.2.0" "matplotlib==3.9.2"
python docs/security-audit/generate_report.py --project "my-app" --findings docs/security-audit/findings.json --format both

# Or directly via skill template (auto-detects, falls back to md)
python skills/security-audit-five/scripts/generate_report.py --project "my-app" --format both
python skills/security-audit-five/scripts/generate_report.py --project "my-app" --format md  # always works
```

## Anti-Patterns (DO NOT)

- `sys.exit(1)` on missing `reportlab` — must fallback to MD.
- Sample routes — enumerate ALL handlers.
- Report without reading file (`rg -n`+`read` required).
- Guess RLS — inspect migration SQL.
- `pip install` global — always `.venv`.
- Omit strengths — coverage proof required.
- Hardcode project name — derive from `package.json#name` or git root.
