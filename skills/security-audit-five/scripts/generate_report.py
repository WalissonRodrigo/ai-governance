#!/usr/bin/env python3
"""
Security Audit Five — Hybrid Report Generator (MD primary, PDF optional)
Template source: skills/security-audit-five/scripts/generate_report.py
Deployed copy : docs/security-audit/generate_report.py
Version 1.1.0 — decoupled: MD always (zero deps), PDF opt-in (isolated venv).

Usage — Mode A (always, zero deps, works in any IDE/sandbox):
  python skills/security-audit-five/scripts/generate_report.py --project "my-app" --format md
  # or
  python docs/security-audit/generate_report.py --project "my-app" --findings findings.json --format md

Usage — Mode B (PDF opt-in, isolated venv — NEVER global):
  python3 -m venv docs/security-audit/.venv
  source docs/security-audit/.venv/bin/activate  # Windows: .venv\\Scripts\\activate
  pip install "reportlab==4.2.0" "matplotlib==3.9.2"
  python docs/security-audit/generate_report.py --project "my-app" --findings findings.json --format both
  # --format pdf  -> PDF only (fails gracefully to MD if deps missing)
  # --format both -> try PDF then MD (recommended)
  # --format md   -> MD only (always succeeds)

If reportlab/matplotlib missing, generator NEVER exits with error — it warns and
produces MD + findings.json, printing the one-liner to regenerate PDF later.

Findings JSON schema (also generated as output):
{
  "project": "my-app",
  "date": "30/08/2026",
  "scope": "src/, supabase/migrations, docker-compose.yml",
  "methodology": "Stack: Next.js+Prisma+Supabase Auth; isolation=RLS ...",
  "findings": [{
    "category": "1. BANCO SEM TRANCA", "severity": "critical",
    "file": "src/routes/orders.ts", "line": "42",
    "snippet": "prisma.order.findMany()", "description": "...",
    "exploitability": "...", "impact": "...",
    "fix": "Adicionar where:{orgId: req.user.orgId}", "acceptance": ["..."]
  }],
  "strengths": ["router X valida posse ..."],
  "weaknesses": ["Risco central ..."],
  "recommendations": [{"priority": "P1", "title": "...", "action": "...", "effort": "4h"}],
  "github_issues": [{
    "title": "[Segurança] ...", "labels": "security, severity:critical",
    "description": "...", "evidence": "src/routes/orders.ts:42", "exploitability": "...",
    "impact": "...", "fix": "...", "acceptance": ["..."]
  }]
}
Missing fields fall back to demo/empty sections — still produces valid MD/PDF.
"""

import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path

# --- Palette (spec-mandated) ---
PALETTE = {
    "critical": "#B91C1C",
    "high": "#EA580C",
    "medium": "#D97706",
    "low": "#2563EB",
    "strength": "#059669",
    "info": "#6B7280",
}
SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
CATEGORY_ORDER = [
    "1. BANCO SEM TRANCA",
    "2. PERMISSÃO NO NAVEGADOR",
    "3. IDOR",
    "4. CHAVES EXPOSTAS",
    "5. INPUTS SEM TRATAMENTO",
]
CATEGORY_SHORT = {
    "1. BANCO SEM TRANCA": "Banco",
    "2. PERMISSÃO NO NAVEGADOR": "Permissão",
    "3. IDOR": "IDOR",
    "4. CHAVES EXPOSTAS": "Secrets",
    "5. INPUTS SEM TRATAMENTO": "XSS",
}

PINNED_DEPS = '"reportlab==4.2.0" "matplotlib==3.9.2"'

def check_deps():
    """Non-fatal dep check. Returns dict with booleans and missing list."""
    have_reportlab = False
    have_matplotlib = False
    missing = []
    try:
        import reportlab  # noqa: F401
        have_reportlab = True
    except ImportError:
        missing.append("reportlab==4.2.0")
    try:
        import matplotlib  # noqa: F401
        have_matplotlib = True
    except ImportError:
        missing.append("matplotlib==3.9.2")
    return {"reportlab": have_reportlab, "matplotlib": have_matplotlib, "missing": missing, "pdf_possible": have_reportlab and have_matplotlib}

def check_deps_warn():
    info = check_deps()
    if info["missing"]:
        print(f"[WARN] PDF deps missing: {', '.join(info['missing'])}", file=sys.stderr)
        print(f"  Mode A (MD) will succeed. For PDF later:", file=sys.stderr)
        print(f"    python3 -m venv docs/security-audit/.venv", file=sys.stderr)
        print(f"    source docs/security-audit/.venv/bin/activate  # Windows: .venv\\Scripts\\activate", file=sys.stderr)
        print(f"    pip install {PINNED_DEPS}", file=sys.stderr)
        print(f"    python docs/security-audit/generate_report.py --format both", file=sys.stderr)
    return info

def load_json(path: Path):
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Failed to parse {path}: {e}", file=sys.stderr)
        return None

def severity_chip_color(sev: str):
    return PALETTE.get(sev.lower(), PALETTE["info"])

def count_by_severity(findings):
    counts = {k: 0 for k in SEVERITY_ORDER}
    for f in findings:
        s = f.get("severity", "info").lower()
        counts[s if s in counts else "info"] += 1
    return counts

def count_by_category(findings):
    counts = {c: 0 for c in CATEGORY_ORDER}
    for f in findings:
        cat = f.get("category", "")
        matched = None
        for c in CATEGORY_ORDER:
            if c.split(".")[0].strip() in cat or cat.strip().upper() in c.upper() or c.upper() in cat.upper():
                matched = c
                break
        if matched:
            counts[matched] += 1
        else:
            if cat.startswith("1"): counts[CATEGORY_ORDER[0]] += 1
            elif cat.startswith("2"): counts[CATEGORY_ORDER[1]] += 1
            elif cat.startswith("3"): counts[CATEGORY_ORDER[2]] += 1
            elif cat.startswith("4"): counts[CATEGORY_ORDER[3]] += 1
            elif cat.startswith("5"): counts[CATEGORY_ORDER[4]] += 1
    return counts

# ─── Charts (only if matplotlib available) ───

def make_charts(findings, out_dir: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sev_counts = count_by_severity(findings)
    cat_counts = count_by_category(findings)
    labels, sizes, colors = [], [], []
    for s in SEVERITY_ORDER:
        if sev_counts[s] > 0:
            labels.append(f"{s} ({sev_counts[s]})")
            sizes.append(sev_counts[s])
            colors.append(PALETTE[s])
    if not sizes:
        labels = ["sem achados"]
        sizes = [1]
        colors = [PALETTE["strength"]]
    out_dir.mkdir(parents=True, exist_ok=True)
    donut_path = out_dir / "_chart_donut.png"
    bar_path = out_dir / "_chart_bar.png"
    plt.figure(figsize=(4.2, 4.2), dpi=170)
    wedges, texts, autotexts = plt.pie(sizes, colors=colors, autopct="%1.0f%%" if sum(sizes)>0 else None, startangle=90, wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.5), textprops=dict(fontsize=8))
    plt.legend(wedges, labels, loc="center", bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=7, frameon=False)
    plt.title("Achados por Severidade", fontsize=10, weight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(donut_path, bbox_inches="tight", transparent=False)
    plt.close()
    cat_labels = [CATEGORY_SHORT[c] for c in CATEGORY_ORDER]
    cat_values = [cat_counts[c] for c in CATEGORY_ORDER]
    bar_colors = ["#334155", "#475569", "#64748B", "#0F766E", "#7C3AED"]
    plt.figure(figsize=(6.2, 3.6), dpi=170)
    bars = plt.bar(cat_labels, cat_values, color=bar_colors, edgecolor="white", linewidth=0.8, width=0.62)
    plt.title("Achados por Categoria", fontsize=10, weight="bold", pad=12)
    plt.ylabel("Quantidade", fontsize=8)
    plt.xticks(fontsize=7, rotation=10, ha="right")
    plt.yticks(fontsize=7)
    for b, v in zip(bars, cat_values):
        if v > 0:
            plt.text(b.get_x()+b.get_width()/2, b.get_height()+0.08, str(v), ha="center", va="bottom", fontsize=8, weight="bold")
    plt.ylim(0, max(1, max(cat_values)+1))
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(bar_path, bbox_inches="tight", transparent=False)
    plt.close()
    return donut_path, bar_path

# ─── Markdown Builder (zero deps, always succeeds) ───

def build_markdown(data, output_path: Path):
    project = data.get("project", Path.cwd().name)
    date_str = data.get("date", datetime.datetime.now().strftime("%d/%m/%Y"))
    scope = data.get("scope", "Escopo auditado: código-fonte completo (backend, frontend, infra)")
    methodology = data.get("methodology", "Nota metodológica: stack detectada automaticamente; cada uma das 5 categorias foi mapeada para o equivalente da stack.")
    findings = data.get("findings", [])
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])
    recommendations = data.get("recommendations", [])
    github_issues = data.get("github_issues", [])
    sev_counts = count_by_severity(findings)
    cat_counts = count_by_category(findings)
    total = len(findings)
    strengths_cnt = len(strengths)

    md = []
    def add(line=""):
        md.append(line)

    # Cover
    add(f"# Relatório de Auditoria de Segurança — {project}")
    add("")
    add(f"> **Data:** {date_str} | **Security Audit Five** | evidências verificadas em código real")
    add("")
    add("---")
    add("")
    add("## Capa — Escopo e Metodologia")
    add("")
    add(f"**Escopo auditado:** {scope}")
    add("")
    add(f"**Nota metodológica:** {methodology}")
    add("")
    add("**Paleta de severidade:** `crítica #B91C1C` | `alta #EA580C` | `média #D97706` | `baixa #2563EB` | `ponto forte #059669` | `info #6B7280`")
    add("")
    add("> Confidencial — uso interno. Evidências: arquivo:linha com trecho verificado.")
    add("")
    # Resumo executivo
    add("## Resumo Executivo")
    add("")
    add(f"**Total de achados:** {total} | **Pontos fortes:** {strengths_cnt} | **Recomendações:** {len(recommendations) if recommendations else (len(findings) if findings else 0)} | **Issues GitHub:** {len(github_issues) if github_issues else total}")
    add("")
    add("### Achados por Severidade")
    add("")
    add("| Severidade | Quantidade | Cor |")
    add("|---|---|---|")
    for sev in SEVERITY_ORDER + ["strength"]:
        if sev == "strength":
            add(f"| FORTE | {strengths_cnt} | {PALETTE['strength']} |")
        else:
            add(f"| {sev.upper()} | {sev_counts[sev]} | {PALETTE[sev]} |")
    add("")
    # ASCII donut placeholder + cat bar as table
    add("### Achados por Categoria")
    add("")
    add("| Categoria | Quantidade |")
    add("|---|---|")
    for c in CATEGORY_ORDER:
        add(f"| {c} | {cat_counts[c]} |")
    add("")
    if total == 0:
        add("_Nenhum achado crítico verificado. Consulte pontos fortes para cobertura._")
    else:
        max_sev = next((s for s in SEVERITY_ORDER if sev_counts[s] > 0), "info")
        cats_hit = [k for k, v in cat_counts.items() if v > 0]
        add(f"_Severidade predominante: **{max_sev}**. Categorias afetadas: {', '.join(cats_hit) or '—'}. Priorize P1._")
    add("")
    # Pontos fortes / fracos
    add("## Pontos Fortes & Pontos Fracos")
    add("")
    add("### Pontos fortes — o que está protegido (com evidência)")
    add("")
    if strengths:
        for i, s in enumerate(strengths, 1):
            add(f"{i}. {s}")
    else:
        add("_Nenhum ponto forte registrado. Adicione verificações positivas para provar cobertura._")
    add("")
    add("### Pontos fracos — riscos centrais")
    add("")
    if weaknesses:
        for i, w in enumerate(weaknesses, 1):
            add(f"{i}. {w}")
    else:
        if findings:
            top = sorted(findings, key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower()) if x.get("severity","info").lower() in SEVERITY_ORDER else 99)[:3]
            for i, f in enumerate(top, 1):
                add(f"{i}. [{f.get('severity','').upper()}] {f.get('category','')} — {f.get('file','')}:{f.get('line','')} — {f.get('description','')}")
        else:
            add("_Nenhum risco central identificado._")
    add("")
    # Achados detalhados
    add("## Achados Detalhados por Categoria")
    add("")
    if not findings:
        add("_Nenhum achado verificável. Auditoria percorreu todos handlers/arquivos relevantes._")
        add("")
    else:
        from collections import defaultdict
        grouped = defaultdict(list)
        for f in findings:
            cat = f.get("category", "Outros")
            norm = cat
            for c in CATEGORY_ORDER:
                if cat.strip().lower() == c.lower() or cat.strip().lower() in c.lower() or c.lower() in cat.strip().lower():
                    norm = c
                    break
            grouped[norm].append(f)
        ordered_cats = [c for c in CATEGORY_ORDER if c in grouped] + [k for k in grouped.keys() if k not in CATEGORY_ORDER]
        for cat in ordered_cats:
            items = grouped[cat]
            items.sort(key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower()) if x.get("severity","info").lower() in SEVERITY_ORDER else 99)
            add(f"### {cat} — {len(items)} achado(s)")
            add("")
            add("| Severidade | Arquivo:linha | Descrição | Código | Explorabilidade |")
            add("|---|---|---|---|---|")
            for f in items:
                sev = f.get("severity","info").upper()
                fl = f"{f.get('file','—')}:{f.get('line','—')}"
                desc = f.get("description","").replace("|","\\|").replace("\n"," ")
                snippet = f.get("snippet","").replace("|","\\|").replace("\n"," ").replace("`","'")[:120]
                expl = f.get("exploitability","").replace("|","\\|").replace("\n"," ")[:100]
                add(f"| {sev} | `{fl}` | {desc} | `{snippet}` | {expl} |")
            add("")
    # Recomendações
    add("## Recomendações Priorizadas")
    add("")
    if not recommendations:
        if findings:
            pri_map = {"critical":"P1","high":"P1","medium":"P2","low":"P3","info":"P3"}
            auto = []
            for f in sorted(findings, key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower()) if x.get("severity","info").lower() in SEVERITY_ORDER else 99):
                sev = f.get("severity","info").lower()
                pri = pri_map.get(sev,"P3")
                title = f"Corrigir {f.get('category','')} em {f.get('file','')}:{f.get('line','')}"
                action = f.get("fix", f.get("description","Aplicar correção conforme evidência."))
                eff = "4h" if pri=="P1" else ("1d" if pri=="P2" else "2d")
                auto.append({"priority":pri,"title":title,"action":action,"effort":eff})
            recommendations = auto[:12]
        else:
            add("_Nenhuma recomendação pendente. Mantenha hardening contínuo (gitleaks, RLS review, IDOR tests)._")
            add("")
            recommendations = []
    if recommendations:
        add("| Prioridade | Recomendação | Esforço |")
        add("|---|---|---|")
        for r in recommendations:
            pri = r.get("priority","P3")
            title = r.get("title","").replace("|","\\|")
            action = r.get("action","").replace("|","\\|").replace("\n"," ")
            eff = r.get("effort","—")
            add(f"| **{pri}** | **{title}** — {action} | {eff} |")
        add("")
        add("_Ordem: P1 → P2 → P3. Valide cada item com teste de regressão._")
        add("")
    # GitHub issues
    add("## ISSUES PARA O GITHUB — Prontas para Copiar e Colar")
    add("")
    add("_Cada bloco entre `--- ISSUE n ---` e `--- FIM ISSUE n ---` é Markdown completo para colar em New Issue. Achados triviais agrupados._")
    add("")
    if not github_issues:
        auto_issues = []
        for f in findings:
            sev = f.get("severity","info").lower()
            title = f.get("github_title", f"[Segurança] {f.get('category','Achado')} — {f.get('file','')}:{f.get('line','')}")
            if not title.startswith("[Segurança]"):
                title = f"[Segurança] {title}"
            body = f"""## Descrição
{f.get('description','Sem descrição.')}

## Evidência — arquivo:linha
`{f.get('file','—')}:{f.get('line','—')}`
```{f.get('lang','')}
{f.get('snippet','')}
```

## Por que é explorável
{f.get('exploitability','Atacante autenticado consegue reproduzir sem validação.')}

## Impacto
{f.get('impact','Vazamento/elevação de privilégio.')}

## Sugestão de correção
{f.get('fix','Aplicar validação de posse/tenant e teste com 2 tenants.')}

## Critérios de aceite
"""
            acc = f.get("acceptance", [])
            if not acc:
                acc = [f"Handler em `{f.get('file','')}:{f.get('line','')}` valida posse/tenant", "Teste automatizado cobre IDOR/tenant isolation", "Nenhum segredo/default exposto"]
            for c in acc:
                body += f"- [ ] {c}\n"
            auto_issues.append({"title":title,"labels":f"security, severity:{sev}","body":body})
        github_issues = auto_issues
    if not github_issues:
        add("_Nenhuma issue gerada — nenhum achado acionável._")
        add("")
    else:
        for idx, issue in enumerate(github_issues, 1):
            add(f"--- ISSUE {idx} ---")
            add("")
            add(f"**Título:** {issue.get('title','[Segurança] Achado')}")
            add("")
            add(f"**Labels sugeridas:** `{issue.get('labels','security')}`")
            add("")
            body = issue.get("body","") or issue.get("description","")
            if not body.strip():
                body = f"## Descrição\n{issue.get('description','')}\n\n## Evidência\n`{issue.get('evidence','')}`\n```\n{issue.get('snippet','')}\n```\n\n## Por que é explorável\n{issue.get('exploitability','')}\n\n## Impacto\n{issue.get('impact','')}\n\n## Sugestão de correção\n{issue.get('fix','')}\n\n## Critérios de aceite\n"
                for c in issue.get("acceptance", []):
                    body += f"- [ ] {c}\n"
            add(body.strip())
            add("")
            add(f"--- FIM ISSUE {idx} ---")
            add("")

    add("---")
    add(f"_Gerado por Security Audit Five v1.1.0 — {project} — {date_str}_")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] MD generated: {output_path} — {len(md)} lines, {output_path.stat().st_size/1024:.1f} KB")
    return output_path

# ─── PDF Builder (requires reportlab+matplotlib) ───

def build_pdf(data, output_path: Path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
    from reportlab.lib.colors import HexColor
    project = data.get("project", Path.cwd().name)
    date_str = data.get("date", datetime.datetime.now().strftime("%d/%m/%Y"))
    scope = data.get("scope", "Escopo auditado: código-fonte completo (backend, frontend, infra)")
    methodology = data.get("methodology", "Nota metodológica: stack detectada automaticamente; cada uma das 5 categorias foi mapeada para o equivalente da stack.")
    findings = data.get("findings", [])
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])
    recommendations = data.get("recommendations", [])
    github_issues = data.get("github_issues", [])
    styles = getSampleStyleSheet()
    s_title = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=22, leading=26, textColor=HexColor("#0F172A"), alignment=TA_CENTER, spaceAfter=6)
    s_h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13, leading=16, textColor=HexColor("#1E293B"), spaceBefore=14, spaceAfter=8, keepWithNext=True)
    s_h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=10.5, leading=14, textColor=HexColor("#334155"), spaceBefore=10, spaceAfter=6, keepWithNext=True)
    s_normal = ParagraphStyle("NormalCustom", parent=styles["Normal"], fontSize=8.5, leading=12.5, textColor=HexColor("#334155"), alignment=TA_JUSTIFY, spaceAfter=4)
    s_small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=7.5, leading=10.5, textColor=HexColor("#475569"), spaceAfter=2)
    s_cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=7, leading=9, textColor=HexColor("#1E293B"))
    s_cell_small = ParagraphStyle("CellSmall", parent=styles["Normal"], fontSize=6.5, leading=8.5, textColor=HexColor("#334155"))
    s_mono = ParagraphStyle("Mono", parent=styles["Normal"], fontSize=6.5, leading=8, textColor=HexColor("#0F172A"), fontName="Courier", backColor=HexColor("#F1F5F9"), borderPadding=(3,3,6), spaceAfter=4)
    s_chip = ParagraphStyle("Chip", parent=styles["Normal"], fontSize=6.5, leading=8, textColor=colors.white, alignment=TA_CENTER)
    s_cover_meta = ParagraphStyle("CoverMeta", parent=styles["Normal"], fontSize=8, leading=11, textColor=HexColor("#64748B"), alignment=TA_CENTER, spaceAfter=2)
    sev_counts = count_by_severity(findings)
    total = len(findings)
    tmp_dir = Path(tempfile.gettempdir()) / "sec_audit_charts"
    donut_path, bar_path = make_charts(findings, tmp_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm, title=f"Relatório de Auditoria de Segurança — {project}", author="Security Audit Five")
    story = []
    w_available = A4[0] - 4*cm
    story.append(Spacer(1, 2.2*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#0F172A"), spaceAfter=12, spaceBefore=6))
    story.append(Paragraph("Relatório de Auditoria de Segurança", ParagraphStyle("CoverTitle1", parent=s_title, fontSize=26, leading=28, textColor=HexColor("#0F172A"), alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph(f"— {project} —", ParagraphStyle("CoverTitle2", parent=s_title, fontSize=18, leading=22, textColor=HexColor("#334155"), alignment=TA_CENTER, spaceAfter=10)))
    story.append(HRFlowable(width="36%", thickness=2, color=HexColor(PALETTE["critical"]), spaceAfter=14, spaceBefore=4, hAlign="CENTER"))
    story.append(Paragraph(f"{date_str} &nbsp;&nbsp;|&nbsp;&nbsp; Security Audit Five &nbsp;&nbsp;|&nbsp;&nbsp; evidências verificadas em código real", s_cover_meta))
    story.append(Spacer(1, 0.7*cm))
    scope_box_data = [[Paragraph(f"<b>Escopo auditado</b><br/>{scope}", s_small)]]
    t_scope = Table(scope_box_data, colWidths=[w_available])
    t_scope.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#F8FAFC")),("BOX",(0,0),(-1,-1),0.6,HexColor("#CBD5E1")),("INNERPADDING",(0,0),(-1,-1),8),("ROUNDEDCORNERS",[3,3,3,3])]))
    story.append(t_scope)
    story.append(Spacer(1, 0.4*cm))
    meth_box = [[Paragraph(f"<b>Nota metodológica</b><br/>{methodology}", s_small)]]
    t_meth = Table(meth_box, colWidths=[w_available])
    t_meth.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#FFF7ED")),("BOX",(0,0),(-1,-1),0.6,HexColor("#FDBA74")),("INNERPADDING",(0,0),(-1,-1),8),("ROUNDEDCORNERS",[3,3,3,3])]))
    story.append(t_meth)
    story.append(Spacer(1, 1.0*cm))
    badge_data = [[Paragraph('<font color="#B91C1C"><b>CRÍTICA</b></font>', s_small), Paragraph('<font color="#EA580C"><b>ALTA</b></font>', s_small), Paragraph('<font color="#D97706"><b>MÉDIA</b></font>', s_small), Paragraph('<font color="#2563EB"><b>BAIXA</b></font>', s_small), Paragraph('<font color="#059669"><b>PONTO FORTE</b></font>', s_small)]]
    t_badges = Table(badge_data, colWidths=[w_available/5]*5)
    t_badges.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),0.4,HexColor("#E2E8F0")),("INNERPADDING",(0,0),(-1,-1),4),("BACKGROUND",(0,0),(-1,-1),colors.white)]))
    story.append(t_badges)
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("Confidencial — uso interno. Evidências: arquivo:linha com trecho verificado. Severidades: crítica/alta/média/baixa/informativa.", ParagraphStyle("Conf", parent=s_small, alignment=TA_CENTER, textColor=HexColor("#94A3B8"))))
    story.append(PageBreak())
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(HexColor("#94A3B8"))
        canvas.drawString(2*cm, A4[1]-1.35*cm, f"Relatório de Auditoria de Segurança — {project}")
        canvas.drawRightString(A4[0]-2*cm, A4[1]-1.35*cm, date_str)
        canvas.setStrokeColor(HexColor("#E2E8F0"))
        canvas.setLineWidth(0.4)
        canvas.line(2*cm, A4[1]-1.55*cm, A4[0]-2*cm, A4[1]-1.55*cm)
        canvas.setFont("Helvetica", 6.5)
        canvas.drawCentredString(A4[0]/2, 1.25*cm, f"página {doc.page}")
        canvas.setFont("Helvetica-Oblique", 6)
        canvas.drawRightString(A4[0]-2*cm, 1.25*cm, "Security Audit Five")
        canvas.restoreState()
    def on_cover(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(HexColor("#94A3B8"))
        canvas.drawCentredString(A4[0]/2, 1.25*cm, f"página {doc.page}")
        canvas.restoreState()
    story.append(Paragraph("Resumo Executivo", s_h1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#E2E8F0"), spaceAfter=6, spaceBefore=2))
    strengths_cnt = len(strengths)
    chip_cells = []
    for sev in SEVERITY_ORDER:
        cnt = sev_counts.get(sev, 0)
        t = Table([[Paragraph(f"<b>{sev.upper()}</b><br/>{cnt}", s_chip)]], colWidths=[w_available/6 -3])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor(PALETTE[sev])),("ROUNDEDCORNERS",[6,6,6,6]),("INNERPADDING",(0,0),(-1,-1),4),("ALIGN",(0,0),(-1,-1),"CENTER")]))
        chip_cells.append(t)
    t_forte2 = Table([[Paragraph(f"<b>FORTE</b><br/>{strengths_cnt}", s_chip)]], colWidths=[w_available/6 -3])
    t_forte2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor(PALETTE["strength"])),("ROUNDEDCORNERS",[6,6,6,6]),("INNERPADDING",(0,0),(-1,-1),4),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    chip_cells.append(t_forte2)
    t_chips = Table([chip_cells], colWidths=[w_available/6 -3]*6, hAlign="CENTER")
    t_chips.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2)]))
    story.append(t_chips)
    story.append(Spacer(1, 4))
    total_para = f"Total de achados: <b>{total}</b> &nbsp;|&nbsp; Pontos fortes: <b>{strengths_cnt}</b> &nbsp;|&nbsp; Recomendações: <b>{len(recommendations)}</b> &nbsp;|&nbsp; Issues: <b>{len(github_issues) if github_issues else total}</b>"
    story.append(Paragraph(total_para, ParagraphStyle("TotalLine", parent=s_small, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8)))
    try:
        img_donut = Image(str(donut_path), width=w_available*0.46, height=w_available*0.46)
        img_bar = Image(str(bar_path), width=w_available*0.52, height=w_available*0.30)
        img_donut.hAlign = "CENTER"
        img_bar.hAlign = "CENTER"
        t_charts = Table([[img_donut, img_bar]], colWidths=[w_available*0.48, w_available*0.52])
        t_charts.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("ALIGN",(0,0),(-1,-1),"CENTER")]))
        story.append(t_charts)
    except Exception as e:
        story.append(Paragraph(f"[Gráficos indisponíveis: {e}]", s_small))
    story.append(Spacer(1, 6))
    if total == 0:
        story.append(Paragraph("Nenhum achado crítico verificado. Consulte pontos fortes para cobertura.", s_normal))
    else:
        max_sev = next((s for s in SEVERITY_ORDER if sev_counts[s] > 0), "info")
        story.append(Paragraph(f"Severidade predominante: <b>{max_sev}</b>. Categorias afetadas: {', '.join([k for k,v in count_by_category(findings).items() if v>0][:3]) or '—'}. Priorize P1.", s_normal))
    story.append(Paragraph("Pontos Fortes &amp; Pontos Fracos", s_h1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#E2E8F0"), spaceAfter=6, spaceBefore=2))
    story.append(Paragraph("Pontos fortes — o que está protegido (com evidência)", ParagraphStyle("PFTitle", parent=s_h2, textColor=HexColor(PALETTE["strength"]))))
    if strengths:
        for idx, st in enumerate(strengths, 1):
            story.append(Paragraph(f"<b>{idx}.</b>  {st}", s_normal))
    else:
        story.append(Paragraph("Nenhum ponto forte registrado. Adicione verificações positivas para provar cobertura.", s_normal))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Pontos fracos — riscos centrais", ParagraphStyle("PWTitle", parent=s_h2, textColor=HexColor(PALETTE["critical"]))))
    if weaknesses:
        for idx, wk in enumerate(weaknesses, 1):
            story.append(Paragraph(f"<b>{idx}.</b>  {wk}", s_normal))
    else:
        if findings:
            top = sorted(findings, key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower()))[:3]
            for idx, f in enumerate(top, 1):
                story.append(Paragraph(f"<b>{idx}.</b>  [{f.get('severity','').upper()}] {f.get('category','')} — {f.get('file','')}:{f.get('line','')} — {f.get('description','')}", s_normal))
        else:
            story.append(Paragraph("Nenhum risco central identificado.", s_normal))
    story.append(Paragraph("Achados Detalhados por Categoria", s_h1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#E2E8F0"), spaceAfter=6, spaceBefore=2))
    if not findings:
        story.append(Paragraph("Nenhum achado verificável. Auditoria percorreu todos handlers/arquivos.", s_normal))
    else:
        from collections import defaultdict
        grouped = defaultdict(list)
        for f in findings:
            cat = f.get("category", "Outros")
            norm = cat
            for c in CATEGORY_ORDER:
                if cat.strip().lower() == c.lower() or cat.strip().lower() in c.lower() or c.lower() in cat.strip().lower():
                    norm = c
                    break
            grouped[norm].append(f)
        ordered_cats = [c for c in CATEGORY_ORDER if c in grouped] + [k for k in grouped.keys() if k not in CATEGORY_ORDER]
        for cat in ordered_cats:
            items = grouped[cat]
            items.sort(key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower()) if x.get("severity","info").lower() in SEVERITY_ORDER else 99)
            story.append(Paragraph(cat, s_h2))
            story.append(Paragraph(f"{len(items)} achado(s) nesta categoria", ParagraphStyle("CatSub", parent=s_small, textColor=HexColor("#64748B"))))
            header = [Paragraph("<b>Sev.</b>", ParagraphStyle("TH", parent=s_small, textColor=colors.white, alignment=TA_CENTER)), Paragraph("<b>Arquivo:linha</b>", ParagraphStyle("TH", parent=s_small, textColor=colors.white, alignment=TA_CENTER)), Paragraph("<b>Descrição</b>", ParagraphStyle("TH", parent=s_small, textColor=colors.white, alignment=TA_CENTER))]
            rows = [header]
            for f in items:
                sev = f.get("severity","info").lower()
                sev_para = Paragraph(f"<b>{sev.upper()}</b>", ParagraphStyle("SevCell", parent=s_cell, textColor=colors.white, alignment=TA_CENTER))
                fl = f"{f.get('file','—')}:{f.get('line','—')}"
                if len(fl) > 42: fl = "…" + fl[-41:]
                fl_para = Paragraph(fl, ParagraphStyle("FLCell", parent=s_cell_small, alignment=TA_CENTER))
                import html as htmlmod
                desc_html = htmlmod.escape(f.get("description",""))
                if f.get("snippet"):
                    desc_html += f"<br/><font face=\"Courier\" size=\"6\" color=\"#0F172A\"><b>Código:</b> <i>{htmlmod.escape(f.get('snippet','')[:160])}</i></font>"
                if f.get("exploitability"):
                    desc_html += f"<br/><font size=\"6\" color=\"#64748B\"><b>Explorabilidade:</b> {htmlmod.escape(f.get('exploitability','')[:120])}</font>"
                desc_para = Paragraph(desc_html, s_cell)
                rows.append([sev_para, fl_para, desc_para])
            col_w = [1.6*cm, 4.4*cm, w_available - 6.0*cm]
            t = Table(rows, colWidths=col_w, repeatRows=1)
            style_cmds = [("BACKGROUND",(0,0),(-1,0),HexColor("#0F172A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ALIGN",(0,0),(-1,0),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("GRID",(0,0),(-1,-1),0.4,HexColor("#CBD5E1")),("INNERPADDING",(0,0),(-1,-1),4),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, HexColor("#F8FAFC")]),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]
            for idx, f in enumerate(items, start=1):
                style_cmds.append(("BACKGROUND",(0, idx),(0, idx),HexColor(severity_chip_color(f.get("severity","info")))))
            t.setStyle(TableStyle(style_cmds))
            story.append(t)
            story.append(Spacer(1, 6))
    story.append(Paragraph("Recomendações Priorizadas", s_h1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#E2E8F0"), spaceAfter=6, spaceBefore=2))
    if not recommendations:
        if findings:
            pri_map = {"critical":"P1","high":"P1","medium":"P2","low":"P3","info":"P3"}
            auto_recs = []
            for f in sorted(findings, key=lambda x: SEVERITY_ORDER.index(x.get("severity","info").lower())):
                pri = pri_map.get(f.get("severity","info").lower(),"P3")
                auto_recs.append({"priority":pri,"title":f"Corrigir {f.get('category','')} em {f.get('file','')}:{f.get('line','')}","action":f.get("fix",f.get("description","Correção conforme evidência.")),"effort":"4h" if pri=="P1" else ("1d" if pri=="P2" else "2d")})
            recommendations = auto_recs[:12]
        else:
            story.append(Paragraph("Nenhuma recomendação pendente. Mantenha hardening contínuo.", s_normal))
            recommendations = []
    if recommendations:
        rec_header = [Paragraph("<b>Prioridade</b>", ParagraphStyle("RTH", parent=s_small, textColor=colors.white, alignment=TA_CENTER)), Paragraph("<b>Recomendação</b>", ParagraphStyle("RTH", parent=s_small, textColor=colors.white, alignment=TA_CENTER)), Paragraph("<b>Esforço</b>", ParagraphStyle("RTH", parent=s_small, textColor=colors.white, alignment=TA_CENTER))]
        rec_rows = [rec_header]
        pri_colors = {"P1":PALETTE["critical"],"P2":PALETTE["medium"],"P3":PALETTE["low"]}
        for r in recommendations:
            pri = r.get("priority","P3")
            pri_para = Paragraph(f"<b>{pri}</b>", ParagraphStyle("PriCell", parent=s_cell, textColor=colors.white, alignment=TA_CENTER))
            import html as htmlmod
            combo = f"<b>{htmlmod.escape(r.get('title',''))}</b><br/><font size=\"7\" color=\"#475569\">{htmlmod.escape(r.get('action',''))}</font>"
            rec_para = Paragraph(combo, s_cell)
            eff_para = Paragraph(htmlmod.escape(r.get("effort","—")), ParagraphStyle("EffCell", parent=s_cell, alignment=TA_CENTER))
            rec_rows.append([pri_para, rec_para, eff_para])
        col_w_rec = [1.8*cm, w_available - 3.6*cm, 1.8*cm]
        t_rec = Table(rec_rows, colWidths=col_w_rec, repeatRows=1)
        rec_style = [("BACKGROUND",(0,0),(-1,0),HexColor("#0F172A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ALIGN",(0,0),(-1,0),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("GRID",(0,0),(-1,-1),0.4,HexColor("#CBD5E1")),("INNERPADDING",(0,0),(-1,-1),4),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, HexColor("#F8FAFC")])]
        for idx, r in enumerate(recommendations, start=1):
            rec_style.append(("BACKGROUND",(0, idx),(0, idx),HexColor(pri_colors.get(r.get("priority","P3"), PALETTE["low"]))))
        t_rec.setStyle(TableStyle(rec_style))
        story.append(t_rec)
        story.append(Spacer(1, 4))
        story.append(Paragraph("Ordem: P1 → P2 → P3. Valide com teste de regressão.", s_small))
    story.append(Paragraph("ISSUES PARA O GITHUB — Prontas para Copiar e Colar", s_h1))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#E2E8F0"), spaceAfter=6, spaceBefore=2))
    story.append(Paragraph("Cada bloco entre <b>--- ISSUE n ---</b> e <b>--- FIM ISSUE n ---</b> é Markdown completo para colar em New Issue.", ParagraphStyle("IssueIntro", parent=s_small, backColor=HexColor("#F1F5F9"), borderPadding=(6,6,6), spaceAfter=8)))
    if not github_issues:
        auto_issues = []
        for f in findings:
            sev = f.get("severity","info").lower()
            title = f.get("github_title", f"[Segurança] {f.get('category','Achado')} — {f.get('file','')}:{f.get('line','')}")
            if not title.startswith("[Segurança]"): title = f"[Segurança] {title}"
            body = f"""## Descrição
{f.get('description','Sem descrição.')}

## Evidência — arquivo:linha
`{f.get('file','—')}:{f.get('line','—')}`
```{f.get('lang','')}
{f.get('snippet','')}
```

## Por que é explorável
{f.get('exploitability','Atacante autenticado consegue reproduzir sem validação.')}

## Impacto
{f.get('impact','Vazamento/elevação de privilégio.')}

## Sugestão de correção
{f.get('fix','Aplicar validação de posse/tenant e teste com 2 tenants.')}

## Critérios de aceite
"""
            acc = f.get("acceptance", [])
            if not acc: acc = [f"Handler em `{f.get('file','')}:{f.get('line','')}` valida posse/tenant","Teste automatizado cobre IDOR/tenant isolation","Nenhum segredo/default exposto"]
            for c in acc: body += f"- [ ] {c}\n"
            auto_issues.append({"title":title,"labels":f"security, severity:{sev}","body":body})
        github_issues = auto_issues
    if not github_issues:
        story.append(Paragraph("Nenhuma issue gerada — nenhum achado acionável.", s_normal))
    else:
        for idx, issue in enumerate(github_issues, 1):
            story.append(Paragraph(f"--- ISSUE {idx} ---", ParagraphStyle("IssueDelim", parent=s_mono, textColor=HexColor("#0F172A"), alignment=TA_CENTER, fontSize=7, leading=9, backColor=HexColor("#E0F2FE"), borderPadding=(4,4,4), spaceAfter=2, spaceBefore=10)))
            title = issue.get("title","[Segurança] Achado sem título")
            labels = issue.get("labels","security")
            body = issue.get("body","") or issue.get("description","")
            if not body.strip():
                import html as htmlmod
                body = f"## Descrição\n{issue.get('description','')}\n\n## Evidência\n`{issue.get('evidence','')}`\n```\n{issue.get('snippet','')}\n```\n\n## Por que é explorável\n{issue.get('exploitability','')}\n\n## Impacto\n{issue.get('impact','')}\n\n## Sugestão de correção\n{issue.get('fix','')}\n\n## Critérios de aceite\n"
                for c in issue.get("acceptance", []): body += f"- [ ] {c}\n"
            story.append(Paragraph(f"<b>Título:</b> {title}", ParagraphStyle("IssueTitle", parent=s_small, textColor=HexColor("#0F172A"), spaceAfter=2)))
            story.append(Paragraph(f"<b>Labels sugeridas:</b> <font color=\"#2563EB\">{labels}</font>", s_small))
            story.append(Spacer(1, 2))
            import html as htmlmod
            body_html = ""
            for line in body.split("\n"):
                esc = htmlmod.escape(line)
                if esc.startswith("## "): esc = f"<b>{esc[3:]}</b>"
                elif esc.startswith("### "): esc = f"<b>{esc[4:]}</b>"
                elif esc.startswith("- [ ]"): esc = f"☐ {esc[5:].strip()}"
                elif esc.startswith("- "): esc = f"• {esc[2:]}"
                body_html += esc + "<br/>"
            body_para = Paragraph(body_html, ParagraphStyle("IssueBody", parent=s_small, fontName="Helvetica", leading=10, textColor=HexColor("#1E293B")))
            t_body = Table([[body_para]], colWidths=[w_available - 6])
            t_body.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#F8FAFC")),("BOX",(0,0),(-1,-1),0.6,HexColor("#CBD5E1")),("INNERPADDING",(0,0),(-1,-1),6),("ROUNDEDCORNERS",[3,3,3,3])]))
            story.append(t_body)
            story.append(Paragraph(f"--- FIM ISSUE {idx} ---", ParagraphStyle("IssueDelimEnd", parent=s_mono, textColor=HexColor("#0F172A"), alignment=TA_CENTER, fontSize=7, leading=9, backColor=HexColor("#E0F2FE"), borderPadding=(4,4,4), spaceBefore=4, spaceAfter=8)))
    try:
        doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)
    except Exception as e:
        print(f"[ERROR] PDF build failed: {e}", file=sys.stderr)
        raise
    pages = None
    try:
        import fitz  # type: ignore
        d = fitz.open(str(output_path))
        pages = len(d)
        d.close()
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore
            reader = PdfReader(str(output_path))
            pages = len(reader.pages)
        except Exception:
            pass
    size_kb = output_path.stat().st_size / 1024
    print(f"[OK] PDF generated: {output_path} — {pages or '?'} pages, {size_kb:.1f} KB")
    if pages and pages < 3:
        print("[WARN] PDF has <3 pages — check if content is too sparse.", file=sys.stderr)
    for p in [donut_path, bar_path]:
        if p.exists():
            try: p.unlink()
            except Exception: pass
    return output_path

def demo_data(project: str):
    return {
        "project": project,
        "date": datetime.datetime.now().strftime("%d/%m/%Y"),
        "scope": "src/, supabase/migrations, docker-compose.yml, .github/workflows, helm/",
        "methodology": "Stack detectada: Next.js 14 + Prisma + Supabase Auth (RLS) + Tailwind; isolamento via RLS policies e filtros `where:{orgId}`; RBAC cruzado frontend↔API; 23 handlers enumerados; secrets em código+compose+CI+Helm+git; XSS em sinks `dangerouslySetInnerHTML`/`innerHTML` e templates de e-mail.",
        "findings": [
            {"category":"1. BANCO SEM TRANCA","severity":"critical","file":"src/routes/orders.ts","line":"42","snippet":"prisma.order.findMany() // sem where orgId","description":"Listagem de pedidos sem filtro por organização/tenant","exploitability":"Autenticado de outra org pode listar todos pedidos","impact":"Vazamento cross-tenant total","fix":"Adicionar where:{orgId: req.user.orgId} em todas queries","acceptance":["Todas queries filtram por orgId","Teste com 2 orgs distintas","Policy RLS alternativa avaliada"]},
            {"category":"3. IDOR","severity":"high","file":"src/routes/users.ts","line":"88","snippet":"prisma.user.findUnique({where:{id}})","description":"Busca por ID sem verificar se objeto pertence ao tenant do chamador","exploitability":"Trocar :id na URL retorna dados de outro tenant","impact":"Exposição de PII cross-tenant","fix":"Verificar obj.orgId === req.user.orgId antes de retornar; 404 se divergir","acceptance":["Check de posse em todos handlers com :id","Teste IDOR automatizado"]},
            {"category":"4. CHAVES EXPOSTAS","severity":"high","file":"docker-compose.yml","line":"15","snippet":"JWT_SECRET: ${JWT_SECRET:-changeme123}","description":"Default público para JWT_SECRET vira segredo real se não sobrescrito; sem validação de startup","exploitability":"Deploy sem .env usa default conhecido → forjaria de tokens","impact":"Comprometimento de autenticação","fix":"Remover default; falhar no startup se JWT_SECRET ausente ou placeholder","acceptance":["Startup rejeita default","CI verifica ausência de fallback"]},
            {"category":"5. INPUTS SEM TRATAMENTO","severity":"medium","file":"src/components/Comment.tsx","line":"27","snippet":"dangerouslySetInnerHTML={{__html: comment.body}}","description":"Renderização de markdown/HTML sem sanitização via DOMPurify","exploitability":"Usuário malicioso injeta <script> armazenado","impact":"XSS armazenado","fix":"Sanitizar com DOMPurify.sanitize(marked.parse(body)) antes do innerHTML","acceptance":["Sanitização aplicada em todos sinks","Teste XSS payload bloqueado"]},
        ],
        "strengths": [
            "Vector 2 — Verificado correto: middleware `src/middleware/rbac.ts:14` valida role `admin` em todas as 8 rotas /admin; gates `isAdmin` em `src/components/AdminPanel.tsx:22` são redundantes apenas.",
            "Vector 4 — Nenhum segredo commitado no histórico git (verificado com `git log -p -S secret`); .env.example sem valores reais.",
            "Vector 1 — RLS habilitada em 4/5 tabelas críticas (`orders`, `users`, `invoices`, `workspaces`) com policies `auth.uid()=user_id`."
        ],
        "weaknesses": [
            "Isolamento de tenant incompleto: 1 listagem (`orders`) e 1 lookup por ID (`users/:id`) sem filtro de posse.",
            "Segredos com defaults inseguros em docker-compose e helm values; ausência de fail-fast no boot.",
            "Sink XSS único com markdown sem sanitização em componente de comentários."
        ],
        "recommendations": [
            {"priority":"P1","title":"Corrigir filtro tenant em orders e IDOR em users","action":"Adicionar where orgId + check de posse em todos handlers; testes cross-tenant.","effort":"1d"},
            {"priority":"P1","title":"Eliminar defaults de segredo e adicionar validação de startup","action":"Remover `:-default` em compose/helm; erro se env ausente.","effort":"4h"},
            {"priority":"P2","title":"Sanitizar markdown em Comment.tsx","action":"Introduzir DOMPurify e aplicar em todos sinks `dangerouslySetInnerHTML`/`v-html`/`innerHTML`.","effort":"4h"},
            {"priority":"P3","title":"Adicionar CI gate para secrets (gitleaks) e RLS lint","action":"Workflow que falha se secret ou RLS ausente.","effort":"2h"},
        ],
        "github_issues": []
    }

def main():
    ap = argparse.ArgumentParser(description="Security Audit Five — Hybrid (MD always, PDF opt-in)")
    ap.add_argument("--project", default=Path.cwd().name, help="Nome do projeto (default: pasta atual)")
    ap.add_argument("--findings", type=str, default=None, help="Path to findings JSON (input). If omitted, uses demo data.")
    ap.add_argument("--output", type=str, default=None, help="Output path (default auto: docs/security-audit/relatorio...pdf or .md based on --format)")
    ap.add_argument("--format", choices=["pdf","md","both"], default="both", help="Output format: pdf (needs deps, fallback to md on fail), md (always), both (try pdf then md) [default: both]")
    ap.add_argument("--date", type=str, default=None, help="Data DD/MM/YYYY (default: hoje)")
    ap.add_argument("--scope", type=str, default=None, help="Override scope text")
    ap.add_argument("--methodology", type=str, default=None, help="Override methodology note")
    args = ap.parse_args()

    # Load data
    data = None
    if args.findings:
        p = Path(args.findings)
        data = load_json(p)
        if data is None:
            print(f"[WARN] Findings JSON not found/invalid at {p} — using demo data.", file=sys.stderr)
            data = demo_data(args.project)
        else:
            if isinstance(data, list):
                data = {"findings": data}
            data.setdefault("project", args.project)
            if args.date: data["date"] = args.date
            elif "date" not in data: data["date"] = datetime.datetime.now().strftime("%d/%m/%Y")
            if args.scope: data["scope"] = args.scope
            if args.methodology: data["methodology"] = args.methodology
    else:
        data = demo_data(args.project)
        if args.date: data["date"] = args.date
        if args.scope: data["scope"] = args.scope
        if args.methodology: data["methodology"] = args.methodology
        if args.format in ("pdf","both"):
            print("[INFO] No --findings supplied — generating with demo data (replace with real audit JSON).", file=sys.stderr)

    data["project"] = data.get("project") or args.project

    # Resolve output paths
    base_dir = Path.cwd() / "docs" / "security-audit"
    base_dir.mkdir(parents=True, exist_ok=True)
    # Also ensure generator copy exists for later regeneration (always)
    try:
        deployed = base_dir / "generate_report.py"
        if Path(__file__).resolve() != deployed.resolve() and not deployed.exists():
            import shutil
            shutil.copy2(Path(__file__), deployed)
            print(f"[INFO] Copied generator to {deployed} for regeneration.")
    except Exception:
        pass

    # Determine requested outputs
    want_pdf = args.format in ("pdf","both")
    want_md = args.format in ("md","both")

    # Resolve explicit --output override
    if args.output:
        out_pdf = Path(args.output) if args.output.endswith(".pdf") else None
        out_md = Path(args.output) if args.output.endswith(".md") else None
        # If user passed explicit path and format both, derive sibling
        if args.format == "both" and args.output:
            if args.output.endswith(".pdf"):
                out_pdf = Path(args.output)
                out_md = Path(str(args.output).replace(".pdf",".md"))
            elif args.output.endswith(".md"):
                out_md = Path(args.output)
                out_pdf = Path(str(args.output).replace(".md",".pdf"))
            else:
                out_pdf = Path(str(args.output) + ".pdf")
                out_md = Path(str(args.output) + ".md")
        elif args.format == "pdf":
            out_pdf = Path(args.output)
        elif args.format == "md":
            out_md = Path(args.output)
    else:
        out_pdf = base_dir / "relatorio-auditoria-seguranca.pdf"
        out_md = base_dir / "relatorio-auditoria-seguranca.md"

    # Also always dump findings.json as structured source (if not already present)
    findings_out = base_dir / "findings.json"
    try:
        if not findings_out.exists():
            findings_out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[OK] findings.json: {findings_out}")
    except Exception as e:
        print(f"[WARN] Could not write findings.json: {e}", file=sys.stderr)

    # ── Mode A: MD always ──
    md_result = None
    if want_md:
        try:
            md_target = out_md if not args.output or args.format != "pdf" else base_dir / "relatorio-auditoria-seguranca.md"
            # If --format both and no explicit output, md_target is out_md
            if args.format == "both" and not args.output:
                md_target = out_md
            elif args.format == "md":
                md_target = out_md if args.output else base_dir / "relatorio-auditoria-seguranca.md"
                if args.output and not str(args.output).endswith(".md"):
                    md_target = Path(str(args.output))
            md_result = build_markdown(data, md_target if isinstance(md_target, Path) else Path(md_target))
        except Exception as e:
            print(f"[ERROR] MD build failed: {e}", file=sys.stderr)
            import traceback; traceback.print_exc()

    # ── Mode B: PDF opt-in (non-blocking) ──
    pdf_result = None
    if want_pdf:
        deps = check_deps()
        if not deps["pdf_possible"]:
            check_deps_warn()
            print("[INFO] Skipping PDF — MD already generated. Regenerate PDF later with:", file=sys.stderr)
            print(f"  pip install {PINNED_DEPS} && python {base_dir/'generate_report.py'} --format pdf", file=sys.stderr)
            if args.format == "pdf" and md_result is None:
                # Fallback: ensure at least MD is produced even when user asked pdf only but deps missing
                try:
                    fallback_md = base_dir / "relatorio-auditoria-seguranca.md"
                    if not fallback_md.exists():
                        build_markdown(data, fallback_md)
                        print(f"[FALLBACK] MD generated at {fallback_md} (PDF deps missing)", file=sys.stderr)
                except Exception as e:
                    print(f"[WARN] Fallback MD also failed: {e}", file=sys.stderr)
            # Do not exit with error — audit succeeded via Mode A
        else:
            try:
                pdf_target = out_pdf if isinstance(out_pdf, Path) else Path(out_pdf)
                if args.format == "md":
                    pdf_target = None
                if pdf_target:
                    pdf_result = build_pdf(data, pdf_target)
            except Exception as e:
                print(f"[WARN] PDF build failed (non-blocking): {e}", file=sys.stderr)
                import traceback; traceback.print_exc()
                print("[INFO] MD already generated — audit succeeded in Mode A.", file=sys.stderr)
                # Ensure MD exists as fallback
                try:
                    fallback_md = base_dir / "relatorio-auditoria-seguranca.md"
                    if not fallback_md.exists() and md_result is None:
                        build_markdown(data, fallback_md)
                except Exception:
                    pass

    # Summary
    print("[DONE] Hybrid generation complete.")
    if md_result: print(f"[DONE] MD: {md_result}")
    if pdf_result: print(f"[DONE] PDF: {pdf_result}")
    elif want_pdf and not pdf_result:
        print(f"[INFO] PDF not generated (deps missing or --format md). MD is primary deliverable.")
    # Ensure exit 0 even if PDF skipped — audit is complete
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
