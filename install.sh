#!/usr/bin/env bash
# Universal AI Agent Config Installer
# Compatible with bash 3.2+ (macOS default) and bash 4+ (Linux/WSL)
set -eu
set -o pipefail 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ──────────────────────────────────────────────────────────────
# Platform detection
# ──────────────────────────────────────────────────────────────

SED_INPLACE=(-i)
if [[ "$(uname)" == "Darwin" ]]; then
    SED_INPLACE=(-i '')
fi

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ${NC}  $*"; }
ok()    { echo -e "${GREEN}✅${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠️${NC}  $*"; }
err()   { echo -e "${RED}❌${NC} $*"; }

prompt() {
    local var_name="$1"
    local prompt_msg="$2"
    local default_val="${3:-}"
    local val

    if [[ -n "$default_val" ]]; then
        read -rp "$(echo -e "${BOLD}${prompt_msg}${NC} [${default_val}]: ")" val
        val="${val:-$default_val}"
    else
        read -rp "$(echo -e "${BOLD}${prompt_msg}${NC}: ")" val
    fi

    printf -v "$var_name" '%s' "$val"
}

prompt_yesno() {
    local prompt_msg="$1"
    local default="${2:-n}"
    local resp

    if [[ "$default" == "y" ]]; then
        read -rp "$(echo -e "${BOLD}${prompt_msg}${NC} [Y/n]: ")" resp
        resp="${resp:-y}"
    else
        read -rp "$(echo -e "${BOLD}${prompt_msg}${NC} [y/N]: ")" resp
        resp="${resp:-n}"
    fi

    [[ "$resp" =~ ^[Yy] ]]
}

# cp_or_fail <src> <dest> — copia com verificação de erro
cp_or_fail() {
    local src="$1"
    local dest="$2"
    if cp "$src" "$dest"; then
        return 0
    else
        warn "Falha ao copiar $src → $dest"
        return 1
    fi
}

# cp_dir_or_fail <src_dir>/* <dest_dir> — copia diretório com verificação
cp_dir_or_fail() {
    local src_glob="$1"
    local dest_dir="$2"
    if cp -r "$src_glob" "$dest_dir"; then
        return 0
    else
        warn "Falha ao copiar skills para $dest_dir"
        return 1
    fi
}

# ──────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     AI Governance Bundle — Installer            ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ──────────────────────────────────────────────────────────────
# Flags
# ──────────────────────────────────────────────────────────────

FORCE=0
INTERACTIVE=1
SKIP_MARKITDOWN=0
SKIP_RTK_CHECK=0

for arg in "$@"; do
    case "$arg" in
        --force)           FORCE=1 ;;
        --non-interactive) INTERACTIVE=0 ;;
        --skip-markitdown) SKIP_MARKITDOWN=1 ;;
        --skip-rtk-check)  SKIP_RTK_CHECK=1 ;;
        --help|-h)
            echo "Uso: ./install.sh [OPÇÕES]"
            echo ""
            echo "Opções:"
            echo "  --force            Força a criação em ~/.claude mesmo sem detectar agente"
            echo "  --non-interactive  Pula prompts de configuração (mantém placeholders)"
            echo "  --skip-markitdown  Não instala markitdown"
            echo "  --skip-rtk-check   Não verifica se rtk está instalado"
            echo "  --help             Mostra esta ajuda"
            exit 0
            ;;
        *)
            warn "Flag desconhecida: $arg (use --help)"
            ;;
    esac
done

# ──────────────────────────────────────────────────────────────
# Fase 0 — Validação de arquivos-fonte
# ──────────────────────────────────────────────────────────────

REQUIRED_FILES=(
    "$SCRIPT_DIR/CLAUDE.md"
    "$SCRIPT_DIR/RULES.md"
    "$SCRIPT_DIR/SKILLS.md"
    "$SCRIPT_DIR/RTK.md"
    "$SCRIPT_DIR/settings.json"
)

MISSING=0
for f in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$f" ]]; then
        err "Arquivo obrigatório ausente: $f"
        MISSING=1
    fi
done

if [[ ! -d "$SCRIPT_DIR/skills" ]]; then
    err "Diretório de skills ausente: $SCRIPT_DIR/skills"
    MISSING=1
fi

if [[ "$MISSING" -eq 1 ]]; then
    echo ""
    err "Repositório incompleto. Clone novamente ou verifique a integridade."
    exit 1
fi

ok "Arquivos-fonte validados."

# ──────────────────────────────────────────────────────────────
# Fase 1 — Coleta de placeholders (interativo)
# ──────────────────────────────────────────────────────────────

# Arrays paralelas (compatível com bash 3.2)
PH_KEYS=()
PH_VALUES=()

if [[ "$INTERACTIVE" -eq 1 ]]; then
    echo ""
    echo -e "${BOLD}── Configuração de perfil ──${NC}"
    echo "Preencha os dados abaixo (Enter mantém o valor padrão entre colchetes):"
    echo ""

    prompt USER_NAME           "Seu nome"                         "Walisson Rodrigo"
    prompt PROFESSIONAL_ROLE   "Cargo/role"                       "Senior Software Architect & Engineer"
    prompt PRIMARY_COMPANY     "Empresa"                          "WR Systems"
    prompt CLIENT_NAME_A       "Cliente A (ou vazio para pular)"  ""
    prompt CLIENT_NAME_B       "Cliente B (ou vazio para pular)"  ""
    prompt CLIENT_NAME_C       "Cliente C (ou vazio para pular)"  ""

    echo ""
    echo -e "${BOLD}── Configuração Git/GitHub ──${NC}"
    echo ""

    prompt PERSONAL_GITHUB_USER "GitHub user pessoal"              ""
    prompt WORK_GITHUB_USER     "GitHub user trabalho (ou vazio)"  ""
    prompt PERSONAL_WORKSPACE   "Workspace pessoal (path host)"    ""
    prompt WORK_WORKSPACE       "Workspace trabalho (ou vazio)"    ""
    prompt NON_CODE_DIR         "Dir não-código (ou vazio)"        ""
    prompt HOST_OS_TYPE         "OS host"                          "Windows"

    PH_KEYS=(
        "<USER_NAME>"
        "<PROFESSIONAL_ROLE>"
        "<PRIMARY_COMPANY>"
        "<CLIENT_NAME_A>"
        "<CLIENT_NAME_B>"
        "<CLIENT_NAME_C>"
        "<PERSONAL_GITHUB_USER>"
        "<WORK_GITHUB_USER>"
        "<PERSONAL_WORKSPACE>"
        "<WORK_WORKSPACE>"
        "<NON_CODE_DIR>"
        "<HOST_OS_TYPE>"
    )
    PH_VALUES=(
        "$USER_NAME"
        "$PROFESSIONAL_ROLE"
        "$PRIMARY_COMPANY"
        "${CLIENT_NAME_A:-N/A}"
        "${CLIENT_NAME_B:-N/A}"
        "${CLIENT_NAME_C:-N/A}"
        "${PERSONAL_GITHUB_USER:-N/A}"
        "${WORK_GITHUB_USER:-N/A}"
        "${PERSONAL_WORKSPACE:-N/A}"
        "${WORK_WORKSPACE:-N/A}"
        "${NON_CODE_DIR:-N/A}"
        "$HOST_OS_TYPE"
    )

    echo ""
    ok "Placeholders coletados."
else
    info "Modo não-interativo: placeholders não serão substituídos."
fi

# ──────────────────────────────────────────────────────────────
# Fase 2 — Detecção de agentes
# ──────────────────────────────────────────────────────────────

TARGET_DIRS=(
    "$HOME/.agents"
    "$HOME/.claude"
    "$HOME/.config/opencode"
    "$HOME/.copilot"
    "$HOME/.devin"
    "$HOME/.gemini"
    "$HOME/.opencode"
    "$HOME/.trae"
    "$HOME/.windsurf"
)

INSTALLED=0
INSTALLED_TARGETS=()
COPY_ERRORS=0

for TARGET in "${TARGET_DIRS[@]}"; do
    if [[ -d "$TARGET" ]] || [[ "$FORCE" -eq 1 && "$TARGET" == "$HOME/.claude" ]]; then
        echo ""
        ok "Ambiente detectado: $TARGET"
        mkdir -p "$TARGET/skills"

        # Copia regras, memórias globais e guia RTK
        for f in CLAUDE.md RULES.md SKILLS.md RTK.md; do
            cp_or_fail "$SCRIPT_DIR/$f" "$TARGET/" || COPY_ERRORS=1
        done

        # Copia settings.json (apenas se não existir no destino)
        if [[ ! -f "$TARGET/settings.json" ]]; then
            cp_or_fail "$SCRIPT_DIR/settings.json" "$TARGET/" || COPY_ERRORS=1
        else
            info "settings.json já existe em $TARGET — pulado."
        fi

        # Copia todas as skills
        cp_dir_or_fail "$SCRIPT_DIR/skills/"* "$TARGET/skills/" || COPY_ERRORS=1

        # Substitui placeholders em RULES.md no destino
        if [[ "$INTERACTIVE" -eq 1 && -f "$TARGET/RULES.md" ]]; then
            RULES_DEST="$TARGET/RULES.md"
            for i in "${!PH_KEYS[@]}"; do
                placeholder="${PH_KEYS[$i]}"
                value="${PH_VALUES[$i]}"
                # Escapa caracteres especiais para sed (delimitador |)
                escaped_value=$(printf '%s\n' "$value" | sed 's/[&/|\]/\\&/g')
                sed "${SED_INPLACE[@]}" "s|${placeholder}|${escaped_value}|g" "$RULES_DEST"
            done
            ok "Placeholders substituídos em $RULES_DEST"
        fi

        ok "Arquivos copiados para $TARGET"
        INSTALLED=1
        INSTALLED_TARGETS+=("$TARGET")
    fi
done

if [[ "$INSTALLED" -eq 0 ]]; then
    echo ""
    err "Nenhum diretório de agente IA padrão foi encontrado."
    echo "Use './install.sh --force' para forçar a criação no ~/.claude"
    exit 1
fi

if [[ "$COPY_ERRORS" -eq 1 ]]; then
    echo ""
    warn "Algumas cópias falharam. Verifique as mensagens acima."
fi

# ──────────────────────────────────────────────────────────────
# Fase 3 — Dependência markitdown
# ──────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}── Dependência: markitdown ──${NC}"

if [[ "$SKIP_MARKITDOWN" -eq 1 ]]; then
    info "Instalação de markitdown pulada (--skip-markitdown)."
elif ! command -v python3 &>/dev/null; then
    warn "python3 não encontrado — markitdown não instalado."
    echo "  Instale Python 3.9+ e execute: pip install markitdown"
elif ! python3 -m pip --version &>/dev/null; then
    warn "pip não disponível para python3 — markitdown não instalado."
    echo "  Instale pip e execute: python3 -m pip install markitdown"
else
    info "Instalando markitdown..."
    MARKITDOWN_ERR=""
    if MARKITDOWN_ERR=$(python3 -m pip install --user markitdown 2>&1); then
        ok "markitdown instalado."
    else
        # PEP 668: externally-managed-environment (Python 3.12+ em Debian/Ubuntu)
        if echo "$MARKITDOWN_ERR" | grep -q 'externally-managed-environment'; then
            info "Python externally-managed (PEP 668) — tentando com --break-system-packages..."
            if MARKITDOWN_ERR=$(python3 -m pip install --user --break-system-packages markitdown 2>&1); then
                ok "markitdown instalado (--break-system-packages)."
            elif command -v pipx &>/dev/null; then
                info "Tentando via pipx..."
                if pipx install markitdown 2>/dev/null; then
                    ok "markitdown instalado via pipx."
                else
                    warn "Falha ao instalar markitdown via pipx."
                    echo "  Instale manualmente: pipx install markitdown"
                    echo "  Ou: python3 -m pip install --user --break-system-packages markitdown"
                fi
            else
                warn "Falha ao instalar markitdown."
                echo "  Python externally-managed (PEP 668). Opções:"
                echo "    1. pipx install markitdown  (recomendado — instale pipx primeiro)"
                echo "    2. python3 -m pip install --user --break-system-packages markitdown"
                echo "    3. Crie um venv: python3 -m venv ~/.venv && ~/.venv/bin/pip install markitdown"
            fi
        else
            warn "Falha ao instalar markitdown."
            echo "  Saída do pip:"
            echo "$MARKITDOWN_ERR" | sed 's/^/    /'
            echo "  Instale manualmente: python3 -m pip install markitdown"
        fi
    fi
fi

# ──────────────────────────────────────────────────────────────
# Fase 3.5 — Dependência ripgrep (rg)
# ──────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}── Dependência: ripgrep (rg) ──${NC}"

if command -v rg &>/dev/null; then
    RG_VERSION=$(rg --version 2>/dev/null | head -1 || echo "desconhecida")
    ok "ripgrep encontrado: $RG_VERSION"
else
    warn "ripgrep (rg) não encontrado no PATH."
    echo "  rg é o motor de busca preferido para análise de código (mais rápido e preciso que grep)."

    if [[ "$INTERACTIVE" -eq 1 ]]; then
        if prompt_yesno "Deseja instalar ripgrep agora?"; then
            RG_INSTALL_OK=0
            OS_TYPE="$(uname -s)"

            if [[ "$OS_TYPE" == "Darwin" ]] && command -v brew &>/dev/null; then
                info "Instalando via Homebrew..."
                if brew install ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "brew install ripgrep falhou."
                fi
            elif command -v apt-get &>/dev/null; then
                info "Instalando via apt..."
                if sudo apt-get update -qq && sudo apt-get install -y -qq ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "apt install ripgrep falhou."
                fi
            elif command -v dnf &>/dev/null; then
                info "Instalando via dnf..."
                if sudo dnf install -y ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "dnf install ripgrep falhou."
                fi
            elif command -v pacman &>/dev/null; then
                info "Instalando via pacman..."
                if sudo pacman -S --noconfirm ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "pacman install ripgrep falhou."
                fi
            elif command -v zypper &>/dev/null; then
                info "Instalando via zypper..."
                if sudo zypper install -y ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "zypper install ripgrep falhou."
                fi
            elif command -v cargo &>/dev/null; then
                info "Instalando via cargo..."
                if cargo install ripgrep; then
                    RG_INSTALL_OK=1
                else
                    warn "cargo install ripgrep falhou."
                fi
            fi

            if [[ "$RG_INSTALL_OK" -eq 1 ]]; then
                hash -r 2>/dev/null || true
                if command -v rg &>/dev/null; then
                    ok "ripgrep instalado com sucesso!"
                else
                    warn "ripgrep instalado mas não detectado no PATH atual."
                    echo "  Abra um novo terminal e execute: rg --version"
                fi
            else
                warn "Não foi possível instalar ripgrep automaticamente."
                echo "  Instale manualmente: https://github.com/BurntSushi/ripgrep#installation"
            fi
        else
            info "Instalação de ripgrep pulada."
            echo "  Instale manualmente: https://github.com/BurntSushi/ripgrep#installation"
        fi
    else
        info "Modo não-interativo: instalação de ripgrep pulada."
        echo "  Instale manualmente: https://github.com/BurntSushi/ripgrep#installation"
    fi
fi

# ──────────────────────────────────────────────────────────────
# Função: remover hook RTK do settings.json sem corromper JSON
# ──────────────────────────────────────────────────────────────

remove_rtk_hook() {
    local settings_file="$1"
    if [[ ! -f "$settings_file" ]]; then
        return 0
    fi

    # Verifica se o hook existe no arquivo
    if ! grep -q 'rtk hook claude' "$settings_file" 2>/dev/null; then
        return 0
    fi

    # Método 1: jq (preferido — garante JSON válido)
    if command -v jq &>/dev/null; then
        local tmp_file="${settings_file}.tmp"
        if jq 'del(.hooks.PreToolUse[] | select(.hooks[]?.command == "rtk hook claude")) | if (.hooks.PreToolUse | length) == 0 then del(.hooks.PreToolUse) else . end | if (.hooks | length) == 0 then del(.hooks) else . end' "$settings_file" > "$tmp_file" 2>/dev/null; then
            # Valida que o resultado é JSON válido antes de sobrescrever
            if jq empty "$tmp_file" 2>/dev/null; then
                mv "$tmp_file" "$settings_file"
                ok "Hook rtk removido de $settings_file (via jq)"
                return 0
            fi
        fi
        rm -f "$tmp_file"
    fi

    # Método 2: python3 (fallback robusto)
    if command -v python3 &>/dev/null; then
        if python3 - "$settings_file" << 'PYEOF' 2>/dev/null
import json, sys

settings_file = sys.argv[1]
with open(settings_file) as f:
    data = json.load(f)

hooks = data.get("hooks", {}).get("PreToolUse", [])
filtered = [
    entry for entry in hooks
    if not any(h.get("command") == "rtk hook claude" for h in entry.get("hooks", []))
]

if filtered:
    data["hooks"]["PreToolUse"] = filtered
else:
    data["hooks"].pop("PreToolUse", None)
    if not data["hooks"]:
        data.pop("hooks", None)

with open(settings_file, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print("OK")
PYEOF
        then
            ok "Hook rtk removido de $settings_file (via python3)"
            return 0
        fi
    fi

    # Se chegou aqui, jq e python3 falharam — o JSON já estava corrompido
    warn "Não foi possível remover o hook de $settings_file automaticamente."
    echo "  O arquivo pode estar corrompido. Restaure com:"
    echo "    cp settings.json $settings_file"
    echo "  Depois edite manualmente para remover o bloco do hook RTK."
}

# ──────────────────────────────────────────────────────────────
# Fase 4 — RTK (Rust Token Killer): verificar, instalar e ativar
# ──────────────────────────────────────────────────────────────

RTK_INSTALLED=0

echo ""
echo -e "${BOLD}── RTK (Rust Token Killer) ──${NC}"

if [[ "$SKIP_RTK_CHECK" -eq 1 ]]; then
    info "Verificação de RTK pulada (--skip-rtk-check)."
else
    # 4a — Verificar se já está instalado e é o RTK correto
    if command -v rtk &>/dev/null; then
        if rtk gain &>/dev/null; then
            RTK_VERSION=$(rtk --version 2>/dev/null || echo "desconhecida")
            ok "RTK (Rust Token Killer) encontrado: $RTK_VERSION"
            RTK_INSTALLED=1
        else
            warn "'rtk' encontrado, mas 'rtk gain' falhou — pode ser Rust Type Kit (projeto errado)."
            echo "  Desinstale com: cargo uninstall rtk"
            echo "  Depois reinstale o correto: cargo install --git https://github.com/rtk-ai/rtk rtk"
        fi
    fi

    # 4b — Oferecer instalação se não encontrado
    if [[ "$RTK_INSTALLED" -eq 0 ]]; then
        echo ""
        warn "RTK não encontrado no PATH."
        echo "  RTK comprime saídas de CLI em 60-90%, economizando tokens do agente."
        echo "  Sem RTK, o hook em settings.json quebrará todas as chamadas Bash."
        echo ""

        if [[ "$INTERACTIVE" -eq 1 ]]; then
            if prompt_yesno "Deseja instalar RTK agora?"; then
                OS_TYPE="$(uname -s)"
                ARCH="$(uname -m)"
                RTK_INSTALL_OK=0

                echo ""
                info "Plataforma: $OS_TYPE ($ARCH)"

                # ── Função: baixar e instalar binário pré-compilado ──
                # Uso: rtk_download_binary <asset_pattern> <extract_cmd> <dest_dir>
                rtk_download_binary() {
                    local asset_pattern="$1"
                    local extract_cmd="$2"
                    local dest_dir="$3"
                    local api_url="https://api.github.com/repos/rtk-ai/rtk/releases/latest"
                    local tmp_dir
                    tmp_dir="$(mktemp -d 2>/dev/null || echo "/tmp/rtk-install-$$")"
                    mkdir -p "$tmp_dir"

                    # Consulta API do GitHub para pegar a tag da latest release
                    info "Consultando latest release no GitHub..."
                    local release_json
                    if command -v curl &>/dev/null; then
                        release_json=$(curl -fsSL "$api_url" 2>/dev/null)
                    elif command -v wget &>/dev/null; then
                        release_json=$(wget -qO- "$api_url" 2>/dev/null)
                    else
                        warn "curl/wget não encontrado — não é possível consultar releases."
                        return 1
                    fi

                    # Extrai tag da versão e URL do asset
                    local tag_name asset_url
                    tag_name=$(echo "$release_json" | grep -o '"tag_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
                    asset_url=$(echo "$release_json" | grep -o '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*"' | grep "$asset_pattern" | head -1 | sed 's/.*"browser_download_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

                    if [[ -z "$tag_name" || -z "$asset_url" ]]; then
                        warn "Não foi possível determinar a versão ou asset ($asset_pattern)."
                        return 1
                    fi

                    info "Última versão: $tag_name"
                    info "Baixando: $(basename "$asset_url")..."

                    local archive="$tmp_dir/$(basename "$asset_url")"
                    if command -v curl &>/dev/null; then
                        curl -fsSL -o "$archive" "$asset_url" 2>/dev/null
                    else
                        wget -qO "$archive" "$asset_url" 2>/dev/null
                    fi

                    if [[ ! -s "$archive" ]]; then
                        warn "Download falhou ou arquivo vazio."
                        rm -rf "$tmp_dir"
                        return 1
                    fi

                    # Extrai e instala
                    mkdir -p "$dest_dir"
                    info "Extraindo para: $dest_dir"
                    eval "$extract_cmd" 2>/dev/null

                    if [[ $? -ne 0 ]]; then
                        warn "Falha ao extrair arquivo."
                        rm -rf "$tmp_dir"
                        return 1
                    fi

                    rm -rf "$tmp_dir"
                    ok "Binário instalado em $dest_dir"
                    return 0
                }

                case "$OS_TYPE" in
                    Linux|Darwin)
                        # 1º — curl installer oficial
                        if command -v curl &>/dev/null; then
                            info "Instalando via curl installer oficial..."
                            if curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh; then
                                RTK_INSTALL_OK=1
                            else
                                warn "curl installer falhou."
                            fi
                        fi

                        # 2º — Homebrew
                        if [[ "$RTK_INSTALL_OK" -eq 0 ]] && command -v brew &>/dev/null; then
                            info "Tentando via Homebrew..."
                            if brew install rtk-ai/tap/rtk; then
                                RTK_INSTALL_OK=1
                            else
                                warn "brew install falhou."
                            fi
                        fi

                        # 3º — Binário pré-compilado da latest release
                        if [[ "$RTK_INSTALL_OK" -eq 0 ]]; then
                            local_rtk_bin_dir="$HOME/.local/bin"
                            case "$ARCH" in
                                x86_64|amd64)
                                    if [[ "$OS_TYPE" == "Darwin" ]]; then
                                        asset="rtk-x86_64-apple-darwin.tar.gz"
                                    else
                                        asset="rtk-x86_64-unknown-linux-musl.tar.gz"
                                    fi
                                    ;;
                                aarch64|arm64)
                                    if [[ "$OS_TYPE" == "Darwin" ]]; then
                                        asset="rtk-aarch64-apple-darwin.tar.gz"
                                    else
                                        asset="rtk-aarch64-unknown-linux-gnu.tar.gz"
                                    fi
                                    ;;
                                *)
                                    asset=""
                                    warn "Arquitetura não suportada para binário pré-compilado: $ARCH"
                                    ;;
                            esac

                            if [[ -n "$asset" ]]; then
                                info "Tentando download do binário pré-compilado ($asset)..."
                                if rtk_download_binary "$asset" "tar -xzf \"\$archive\" -C \"\$local_rtk_bin_dir\"" "$local_rtk_bin_dir"; then
                                    # Garante que o diretório está no PATH para esta sessão
                                    case ":$PATH:" in
                                        *":$local_rtk_bin_dir:"*) ;;
                                        *) export PATH="$local_rtk_bin_dir:$PATH" ;;
                                    esac
                                    RTK_INSTALL_OK=1
                                fi
                            fi
                        fi

                        # 4º — Cargo (universal, se Rust instalado)
                        if [[ "$RTK_INSTALL_OK" -eq 0 ]] && command -v cargo &>/dev/null; then
                            info "Tentando via cargo..."
                            if cargo install --git https://github.com/rtk-ai/rtk rtk; then
                                RTK_INSTALL_OK=1
                            else
                                warn "cargo install falhou."
                            fi
                        fi
                        ;;
                    MINGW*|MSYS*|CYGWIN*|Windows*)
                        # Windows — baixar binário pré-compilado automaticamente
                        local_rtk_bin_dir="$HOME/.local/bin"
                        case "$ARCH" in
                            x86_64|amd64)
                                asset="rtk-x86_64-pc-windows-msvc.zip"
                                ;;
                            aarch64|arm64)
                                asset="rtk-aarch64-pc-windows-msvc.zip"
                                ;;
                            *)
                                asset=""
                                warn "Arquitetura não suportada para binário Windows: $ARCH"
                                ;;
                        esac

                        if [[ -n "$asset" ]]; then
                            info "Baixando binário pré-compilado ($asset)..."
                            # No Windows/MSYS2, unzip está disponível; fallback para powershell
                            if command -v unzip &>/dev/null; then
                                if rtk_download_binary "$asset" "unzip -o \"\$archive\" -d \"\$local_rtk_bin_dir\"" "$local_rtk_bin_dir"; then
                                    case ":$PATH:" in
                                        *":$local_rtk_bin_dir:"*) ;;
                                        *) export PATH="$local_rtk_bin_dir:$PATH" ;;
                                    esac
                                    RTK_INSTALL_OK=1
                                fi
                            elif command -v powershell &>/dev/null; then
                                # Fallback: PowerShell Expand-Archive
                                if rtk_download_binary "$asset" "powershell -NoProfile -Command \"Expand-Archive -Path '\$archive' -DestinationPath '\$local_rtk_bin_dir' -Force\"" "$local_rtk_bin_dir"; then
                                    case ":$PATH:" in
                                        *":$local_rtk_bin_dir:"*) ;;
                                        *) export PATH="$local_rtk_bin_dir:$PATH" ;;
                                    esac
                                    RTK_INSTALL_OK=1
                                fi
                            else
                                warn "unzip e powershell não encontrados."
                                echo "  Baixe manualmente: https://github.com/rtk-ai/rtk/releases"
                                echo "  Extraia rtk.exe para: $local_rtk_bin_dir"
                            fi
                        fi

                        # Fallback: Cargo (se Rust instalado)
                        if [[ "$RTK_INSTALL_OK" -eq 0 ]] && command -v cargo &>/dev/null; then
                            if prompt_yesno "Tentar via cargo (se Rust instalado)?"; then
                                info "Instalando via cargo..."
                                if cargo install --git https://github.com/rtk-ai/rtk rtk; then
                                    RTK_INSTALL_OK=1
                                else
                                    warn "cargo install falhou."
                                fi
                            fi
                        fi
                        ;;
                    *)
                        warn "SO não reconhecido: $OS_TYPE"
                        echo "  Instale manualmente: https://github.com/rtk-ai/rtk#installation"
                        ;;
                esac

                # Verificar instalação
                if [[ "$RTK_INSTALL_OK" -eq 1 ]]; then
                    # Recarregar PATH para detectar novo binário
                    hash -r 2>/dev/null || true
                    if command -v rtk &>/dev/null && rtk gain &>/dev/null; then
                        ok "RTK instalado e verificado com sucesso!"
                        RTK_INSTALLED=1
                    else
                        warn "RTK instalado mas não detectado no PATH atual."
                        echo "  Abra um novo terminal e execute: rtk gain"
                        echo "  Ou adicione $HOME/.local/bin ao seu PATH"
                    fi
                else
                    warn "Não foi possível instalar RTK automaticamente."
                    echo "  Instale manualmente: https://github.com/rtk-ai/rtk#installation"
                fi
            else
                # Usuário recusou instalação — oferecer remover hook
                echo ""
                if prompt_yesno "Deseja remover o hook do settings.json para evitar erros?"; then
                    for t in "${INSTALLED_TARGETS[@]}"; do
                        remove_rtk_hook "$t/settings.json"
                    done
                else
                    info "Hook mantido. Instale RTK antes de usar o agente."
                    echo "  Guia: https://github.com/rtk-ai/rtk#installation"
                fi
            fi
        else
            # Modo não-interativo — remover hook automaticamente
            info "Modo não-interativo: removendo hook rtk do settings.json..."
            for t in "${INSTALLED_TARGETS[@]}"; do
                remove_rtk_hook "$t/settings.json"
            done
        fi
    fi

    # 4c — Inicializar hook global do RTK se instalado
    if [[ "$RTK_INSTALLED" -eq 1 ]]; then
        echo ""
        if [[ "$INTERACTIVE" -eq 1 ]]; then
            if prompt_yesno "Executar 'rtk init -g' para ativar o hook global?" "y"; then
                if rtk init -g; then
                    ok "Hook global do RTK ativado."
                else
                    warn "rtk init -g falhou. Execute manualmente após reiniciar o terminal."
                fi
            else
                info "Hook não ativado. Execute 'rtk init -g' quando desejar ativar."
            fi
        else
            info "Execute 'rtk init -g' para ativar o hook global."
        fi
    fi
fi

# ──────────────────────────────────────────────────────────────
# Fase 5 — Developer Tooling (ast-grep, tsc, mypy, pytest)
# ──────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}── Developer Tooling ──${NC}"

# 5a — ast-grep
if command -v ast-grep &>/dev/null; then
    ok "ast-grep encontrado: $(ast-grep --version 2>/dev/null | head -1 || echo "desconhecida")"
else
    warn "ast-grep não encontrado no PATH."
    if [[ "$INTERACTIVE" -eq 1 ]] && prompt_yesno "Deseja instalar ast-grep?"; then
        AG_INSTALL_OK=0

        if command -v cargo &>/dev/null; then
            info "Instalando ast-grep via cargo..."
            if cargo install ast-grep; then
                AG_INSTALL_OK=1
            else
                warn "cargo install ast-grep falhou."
            fi
        elif command -v npm &>/dev/null; then
            info "Instalando ast-grep via npm..."
            if npm install -g @ast-grep/cli; then
                AG_INSTALL_OK=1
            else
                warn "npm install -g @ast-grep/cli falhou."
            fi
        elif command -v brew &>/dev/null; then
            info "Instalando ast-grep via Homebrew..."
            if brew install ast-grep; then
                AG_INSTALL_OK=1
            else
                warn "brew install ast-grep falhou."
            fi
        fi

        hash -r 2>/dev/null || true
        if [[ "$AG_INSTALL_OK" -eq 1 ]] && command -v ast-grep &>/dev/null; then
            ok "ast-grep instalado."
        elif [[ "$AG_INSTALL_OK" -eq 1 ]] && command -v sg &>/dev/null; then
            # algumas distros do npm fornecem 'sg' como binário ast-grep
            mkdir -p "$HOME/.local/bin"
            ln -sf "$(command -v sg)" "$HOME/.local/bin/ast-grep"
            case ":$PATH:" in
                *":$HOME/.local/bin:"*) ;;
                *) export PATH="$HOME/.local/bin:$PATH" ;;
            esac
            ok "ast-grep instalado (link a partir de 'sg')."
        else
            warn "Não foi possível instalar ast-grep automaticamente."
            echo "  Guia: https://ast-grep.github.io"
        fi
    else
        info "ast-grep pulado."
    fi
fi

# 5b — TypeScript (tsc)
if command -v tsc &>/dev/null; then
    ok "tsc (TypeScript) encontrado."
else
    warn "tsc (TypeScript) não encontrado no PATH."
    if [[ "$INTERACTIVE" -eq 1 ]] && prompt_yesno "Deseja instalar TypeScript globalmente?"; then
        if command -v npm &>/dev/null; then
            info "Instalando TypeScript via npm..."
            if npm install -g typescript; then
                hash -r 2>/dev/null || true
                if command -v tsc &>/dev/null; then
                    ok "TypeScript (tsc) instalado."
                else
                    warn "tsc instalado mas não detectado no PATH atual."
                    echo "  Abra um novo terminal ou adicione o diretório npm global ao PATH."
                fi
            else
                warn "npm install -g typescript falhou."
            fi
        else
            warn "npm não encontrado — instale Node.js para obter tsc."
        fi
    else
        info "TypeScript pulado."
    fi
fi

# 5c — Python dev tools (mypy, pytest)
if command -v python3 &>/dev/null && python3 -m pip --version &>/dev/null; then
    if command -v mypy &>/dev/null && command -v pytest &>/dev/null; then
        ok "mypy e pytest encontrados."
    else
        warn "mypy e/ou pytest não encontrados no PATH."
        if [[ "$INTERACTIVE" -eq 1 ]] && prompt_yesno "Deseja instalar mypy e pytest?"; then
            PYDEV_ERR=""
            if PYDEV_ERR=$(python3 -m pip install --user mypy pytest 2>&1); then
                PYDEV_OK=1
            elif echo "$PYDEV_ERR" | grep -q 'externally-managed-environment'; then
                info "Python externally-managed (PEP 668) — tentando com --break-system-packages..."
                if PYDEV_ERR=$(python3 -m pip install --user --break-system-packages mypy pytest 2>&1); then
                    PYDEV_OK=1
                elif command -v pipx &>/dev/null; then
                    info "Tentando via pipx..."
                    if pipx install mypy && pipx install pytest; then
                        PYDEV_OK=1
                    fi
                fi
            fi

            if [[ "${PYDEV_OK:-0}" -eq 1 ]]; then
                case ":$PATH:" in
                    *":$HOME/.local/bin:"*) ;;
                    *) export PATH="$HOME/.local/bin:$PATH" ;;
                esac
                hash -r 2>/dev/null || true
                if command -v mypy &>/dev/null && command -v pytest &>/dev/null; then
                    ok "mypy e pytest instalados."
                else
                    warn "mypy/pytest instalados mas não detectados no PATH atual."
                    echo "  Abra um novo terminal. Em projetos, prefira usar: python3 -m mypy / python3 -m pytest"
                fi
            else
                warn "Falha ao instalar mypy/pytest."
                echo "  Opções:"
                echo "    1. python3 -m pip install --user --break-system-packages mypy pytest"
                echo "    2. pipx install mypy && pipx install pytest"
            fi
        else
            info "mypy e pytest pulados."
        fi
    fi
else
    info "Python 3/pip não encontrado — mypy e pytest não verificados."
fi

# ──────────────────────────────────────────────────────────────
# Resumo final
# ──────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗"
echo "║            Instalação concluída!                 ║"
echo -e "╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo "Destinos instalados:"
for t in "${INSTALLED_TARGETS[@]}"; do
    echo "  • $t"
done
echo ""

if [[ "$INTERACTIVE" -eq 0 ]]; then
    warn "Placeholders NÃO substituídos (modo não-interativo)."
    echo "  Edite RULES.md nos destinos e substitua:"
    echo "  <USER_NAME>, <PROFESSIONAL_ROLE>, <PRIMARY_COMPANY>,"
    echo "  <CLIENT_NAME_*>, <PERSONAL_GITHUB_USER>, <WORK_GITHUB_USER>,"
    echo "  <PERSONAL_WORKSPACE>, <WORK_WORKSPACE>, <NON_CODE_DIR>, <HOST_OS_TYPE>"
fi

echo ""
echo "Próximos passos:"
echo "  1. Substitua os placeholders em RULES.md nos destinos (se modo não-interativo)"
if [[ "$RTK_INSTALLED" -eq 1 ]]; then
    echo "  2. RTK instalado e hook ativado — compressão de tokens ativa"
    echo "  3. Reinicie o terminal para garantir que todas as ferramentas estejam no PATH"
else
    echo "  2. (Opcional) Instale RTK: https://github.com/rtk-ai/rtk#installation"
    echo "  3. Reinicie o terminal para garantir que todas as ferramentas estejam no PATH"
fi
echo ""