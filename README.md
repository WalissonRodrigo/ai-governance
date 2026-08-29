# ~/.claude — Guia de Reuso

Este diretório contém a configuração de agentes de IA (Claude Code, opencode e compatíveis com Agent Skills). Este guia explica o que é reutilizável, o que é específico desta máquina e como reaproveitar cada parte em outro ambiente.

## Inventário

| Arquivo | O que é | Reutilizável? |
| --- | --- | --- |
| `CLAUDE.md` | Memória global do agente; importa `@RTK.md` e `@RULES.md` | Parcialmente (estrutura de imports) |
| `RULES.md` | Regras de governança: arquitetura (SOLID/DDD/TDD), economia de tokens, operações e comunicação | Sim, com adaptações |
| `RTK.md` | Guia do RTK (Rust Token Killer), wrapper de compressão de saída CLI | Sim, apenas se usar `rtk` |
| `skills/smart-doc-converter/` | Skill que converte PDF/Office em Markdown antes da leitura | Sim |
| `settings.json` | Hooks do Claude Code (`rtk hook claude`) | Somente com `rtk` instalado |
| `settings.local.json` | Configuração local (proxy, hooks de ferramentas da máquina) | **Não** — específico desta máquina |

---

## 1. Reutilizando a skill `smart-doc-converter`

Converte documentos binários (`.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`) em Markdown antes da leitura pelo agente, economizando tokens e preservando dados tabulares.

**Instalação** — copie a pasta inteira para um destes locais (o resultado deve ser `<raiz>/smart-doc-converter/SKILL.md`):

| Ferramenta | Global | Por projeto |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| opencode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Agentes `.agents` | `~/.agents/skills/` | `.agents/skills/` |

**Dependências**
- Python 3.9+
- `pip install markitdown` (extras opcionais, ex.: `pip install 'markitdown[pdf]'`)

**Verificação** — reinicie o agente; a skill deve aparecer em `<available_skills>`. Uso manual do script:
```bash
python scripts/convert.py relatorio.pdf                  # gera relatorio.pdf.md
python scripts/convert.py relatorio.pdf .ai-cache/r.md   # saída personalizada
```

Comportamento: cache por mtime (saída mais nova que a fonte → conversão é pulada).

---

## 2. Reutilizando as regras (`RULES.md`)

**Opção A — global:** copie `RULES.md` para `~/.claude/` e importe no seu `CLAUDE.md`:
```markdown
@RULES.md
```

**Opção B — por projeto:** copie para a raiz do repositório e referencie no `CLAUDE.md`/`AGENTS.md` do projeto.

**Pontos a adaptar antes de repassar:**
- §1 *Environment*: a preferência por WSL reflete um setup Windows+WSL; ajuste ao SO do desenvolvedor.
- §1 *RTK*: é opcional; remova se o time não usar `rtk`.
- §6 *Language*: o padrão é `pt-BR`; ajuste o idioma-base do seu time.
- §2 *Confidentiality*: regra genérica de isolamento de clientes; mantenha ou adapte à sua política.

---

## 3. Reutilizando `RTK.md` + hook

- Só faz sentido com `rtk` (Rust Token Killer) instalado: valide com `rtk --version` e `rtk gain`.
- ⚠️ Colisão de nome: `reachingforthejack/rtk` (Rust Type Kit) é outro projeto; confira o binário.
- Hook no `settings.json` (Claude Code):
  ```json
  { "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command", "command": "rtk hook claude" } ] } ] } }
  ```
  **Sem `rtk` instalado, não copie este hook** — toda chamada de ferramenta Bash falharia.

---

## 4. O que NÃO copiar

- `settings.local.json`: contém caminhos absolutos da máquina, hooks de ferramentas locais e URLs de proxy pessoais.
- Qualquer caminho absoluto (`C:\Users\...`, `/home/usuario/...`); prefira `~` ou caminhos relativos.

---

## 5. Setup rápido (Linux/macOS/WSL)

```bash
# 1. Skill
mkdir -p ~/.claude/skills
cp -r smart-doc-converter ~/.claude/skills/
python3 -m pip install --user markitdown

# 2. Regras
cp RULES.md ~/.claude/
printf '\n@RULES.md\n' >> ~/.claude/CLAUDE.md

# 3. (Opcional) RTK — somente se instalado
# adicione o hook "rtk hook claude" no settings.json
```

Para opencode, troque `~/.claude/skills/` por `~/.config/opencode/skills/` no passo 1.

---

## 6. Compatibilidade

| Ferramenta | Descoberta de skills | Regras/memória |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/`, `.claude/skills/` | `CLAUDE.md` com `@imports` |
| opencode | `~/.config/opencode/skills/`, `.opencode/skills/`, `.claude/skills/` | `AGENTS.md` / `CLAUDE.md` |
| Agentes `.agents` | `~/.agents/skills/`, `.agents/skills/` | `AGENTS.md` |

> Pacote sanitizado para distribuição disponível em `docs/skills-share/` (skill + `RULES.md`/`RTK.md` sem dados pessoais).
