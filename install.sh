#!/usr/bin/env bash
# Universal AI Agent Config Installer

echo "🚀 Iniciando instalação do AI Governance Bundle..."

# Define os possíveis diretórios alvo dos agentes mais populares
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

for TARGET in "${TARGET_DIRS[@]}"; do
    if [ -d "$TARGET" ] || [ "$1" == "--force" ]; then
        echo "✅ Ambiente detectado: $TARGET"
        mkdir -p "$TARGET/skills"
        
        # Copia as regras e memórias globais
        cp CLAUDE.md RULES.md SKILLS.md "$TARGET/" 2>/dev/null
        
        # Copia todas as skills
        cp -r skills/* "$TARGET/skills/" 2>/dev/null
        
        echo "   -> Arquivos copiados com sucesso."
        INSTALLED=1
    fi
done

if [ $INSTALLED -eq 0 ]; then
    echo "⚠️ Nenhum diretório de agente IA padrão foi encontrado."
    echo "Use './install.sh --force' para forçar a criação no ~/.claude"
else
    echo "📦 Instalando dependências de skills (markitdown)..."
    python3 -m pip install markitdown --quiet
    
    echo ""
    echo "🎉 Instalação concluída!"
    echo "⚠️ IMPORTANTE: Abra o arquivo RULES.md no seu diretório de instalação e substitua as variáveis <USER_NAME>, <WORKSPACE>, etc., com seus dados reais."
fi