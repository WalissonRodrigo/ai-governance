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

## 🚀 Instalação (Agentic Setup)

A maneira mais fácil de instalar este pacote é pedir para o seu próprio Agente de IA (Claude Code, OpenCode, Devin, Trae) fazer o trabalho pesado.

1. Clone este repositório:
   `git clone https://github.com/seu-usuario/ai-governance-bundle.git`
2. Entre na pasta:
   `cd ai-governance-bundle`
3. Abra seu agente no terminal (ex: `claude` ou `opencode`) e cole exatamente o prompt abaixo:

> **PROMPT PARA COPIAR E COLAR NO AGENTE:**
> "I want to install this AI Governance Bundle as your global configuration. 
> Please execute the following bootstrap sequence:
> 1. **Environment Detection**: Detect which global configuration directory you use (e.g., `~/.claude/`, `~/.config/opencode/`, `~/.agents/`, etc.).
> 2. **Scaffold**: Create the necessary `skills/` directories in your global config path.
> 3. **Copy Files**: Copy `CLAUDE.md`, `RULES.md`, `SKILLS.md` and the entire `skills/` folder from this repository into your global configuration directory.
> 4. **Dependency Installation**: Run `python3 -m pip install markitdown` in my environment.
> 5. **Interactive Customization**: Scan the copied `RULES.md` for any placeholders in the format `<PLACEHOLDER_NAME>` (like `<USER_NAME>`, `<PERSONAL_WORKSPACE>`, etc.). Present me with a numbered list of these placeholders and ask me for the values to replace them with. Wait for my answer, then apply the replacements.
> 6. **Finish**: Confirm when the installation is complete and you are ready to operate under the new rules."

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

- O instalador (`install.sh`) detecta a plataforma e oferece instalar RTK automaticamente (curl installer, Homebrew ou cargo).
- ⚠️ Colisão de nome: `reachingforthejack/rtk` (Rust Type Kit) é outro projeto; o instalador verifica com `rtk gain` para garantir o binário correto.
- Após instalar, o instalador oferece executar `rtk init -g` para ativar o hook global.
- Hook no `settings.json` (Claude Code):
  ```json
  { "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command", "command": "rtk hook claude" } ] } ] } }
  ```
  **Sem `rtk` instalado, não copie este hook** — toda chamada de ferramenta Bash falharia. O instalador remove o hook automaticamente se RTK não for instalado.

---

## 4. O que NÃO copiar

- `settings.local.json`: contém caminhos absolutos da máquina, hooks de ferramentas locais e URLs de proxy pessoais.
- Qualquer caminho absoluto (`C:\Users\...`, `/home/usuario/...`); prefira `~` ou caminhos relativos.

---

## 5. Setup rápido (Linux/macOS/WSL)

### Opção A — Instalador interativo (recomendado)

```bash
chmod +x install.sh
./install.sh
```

O instalador detecta automaticamente os agentes instalados, coleta seus dados de perfil e Git/GitHub via prompts, substitui os placeholders em `RULES.md`, instala `markitdown` (se Python 3.9+ estiver disponível), oferece a instalação do `ripgrep` e do `Developer Tooling` (`ast-grep`, `tsc`, `mypy`, `pytest`) e verifica se o RTK está no PATH — oferecendo remover o hook do `settings.json` se o RTK não for encontrado.

**Flags opcionais:**

| Flag | Descrição |
| --- | --- |
| `--force` | Força a criação em `~/.claude` mesmo sem detectar agente |
| `--non-interactive` | Pula prompts de configuração (mantém placeholders) |
| `--skip-markitdown` | Não instala markitdown |
| `--skip-rtk-check` | Não verifica se RTK está instalado |
| `--help` | Mostra ajuda |

### Opção B — Manual

```bash
# 1. Skill
mkdir -p ~/.claude/skills
cp -r skills/smart-doc-converter ~/.claude/skills/
python3 -m pip install --user markitdown

# 2. Regras + RTK + Skills
cp CLAUDE.md RULES.md SKILLS.md RTK.md ~/.claude/
cp -r skills/* ~/.claude/skills/

# 3. RTK (recomendado)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
rtk init -g    # ativa hook no settings.json
rtk gain       # verifica instalação correta

# 4. Ferramentas de análise (recomendado)
brew install ast-grep ripgrep    # macOS/Linux com Homebrew
# ou: cargo install ast-grep     # Rust
npm install -g typescript        # tsc
python3 -m pip install --user mypy pytest
```

---

## 6. Compatibilidade

| Ferramenta | Diretório global | Descoberta de skills | Regras/memória |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/` | `skills/`, `.claude/skills/` | `CLAUDE.md` com `@imports` |
| opencode | `~/.config/opencode/` | `skills/`, `.opencode/skills/` | `AGENTS.md` / `CLAUDE.md` |
| Agentes `.agents` | `~/.agents/` | `skills/`, `.agents/skills/` | `AGENTS.md` |
| Devin | `~/.devin/` | `skills/` | `CLAUDE.md` / `AGENTS.md` |
| GitHub Copilot | `~/.copilot/` | `skills/` | `CLAUDE.md` |
| Gemini CLI | `~/.gemini/` | `skills/` | `CLAUDE.md` |
| Trae | `~/.trae/` | `skills/` | `CLAUDE.md` |

> Pacote sanitizado para distribuição disponível em `docs/skills-share/` (skill + `RULES.md`/`RTK.md` sem dados pessoais).

---

## 7. Dependências instaladas pelo `install.sh`

| Ferramenta | Propósito | Método de instalação | Obrigatória? |
| --- | --- | --- | --- |
| `markitdown` | Conversão de docs binários → Markdown | `pip install --user markitdown` | Recomendada |
| `ripgrep` (`rg`) | Busca de código rápida | brew/apt/dnf/pacman/zypper/cargo | Recomendada |
| `ast-grep` | Busca semântica por AST | cargo/npm/brew | Opcional |
| `tsc` (TypeScript) | Type-checking TypeScript | `npm install -g typescript` | Opcional |
| `mypy` | Type-checking Python | `pip install --user mypy` | Opcional |
| `pytest` | Framework de testes Python | `pip install --user pytest` | Opcional |
| `rtk` (Rust Token Killer) | Compressão de saída CLI (60-90% tokens) | curl installer/brew/cargo/binary | Opcional |

---

## 8. Troubleshooting

### `install.sh: line X: $'\r': command not found`

O arquivo tem line endings CRLF (Windows). O repositório inclui `.gitattributes` para forçar LF, mas se você editou o arquivo no Windows:

```bash
# Fix rápido (uma vez):
sed -i 's/\r$//' install.sh
# Ou:
dos2unix install.sh
```

### `markitdown` falhou na instalação

O instalador exibe a saída do `pip` para diagnóstico e tenta fallbacks automáticos. Causas comuns:
- **Python < 3.9**: `markitdown` requer 3.9+. Verifique com `python3 --version`.
- **pip ausente**: Instale com `sudo apt install python3-pip` (Linux) ou `brew install python` (macOS).
- **PEP 668 (`externally-managed-environment`)**: Python 3.12+ em Debian/Ubuntu bloqueia `pip install --user`. O instalador tenta automaticamente `--break-system-packages` e `pipx`. Se ambos falharem:

  ```bash
  # Opção 1: pipx (recomendado)
  sudo apt install pipx
  pipx install markitdown

  # Opção 2: --break-system-packages
  python3 -m pip install --user --break-system-packages markitdown

  # Opção 3: venv
  python3 -m venv ~/.venv
  ~/.venv/bin/pip install markitdown
  ```

### RTK não encontrado — hook removido

Se o RTK não estiver no PATH, o instalador remove o hook do `settings.json` automaticamente (modo não-interativo) ou pergunta (modo interativo). O hook é removido com segurança usando `jq` ou `python3`, preservando o JSON válido.

Para instalar RTK depois:

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
rtk init -g    # reativa o hook
rtk gain       # verifica
```

### Placeholders não substituídos

No modo `--non-interactive`, os placeholders `<USER_NAME>`, `<PROFESSIONAL_ROLE>`, etc. não são preenchidos. Edite `RULES.md` manualmente nos destinos ou rode `./install.sh` sem `--non-interactive`.

### Windows (PowerShell/CMD)

O `install.sh` é um script bash e não roda nativamente no PowerShell/CMD. Use WSL:

```powershell
wsl bash install.sh
```
Se o WSL não estiver instalado:

```powershell
wsl --install
```
