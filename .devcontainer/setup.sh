#!/bin/bash
set -e

echo "🔧 Configurando ambiente sap-ariba-mcp..."

WORKSPACE_DIR="/workspaces/sap-ariba-mcp"

# 1. Instalar dependências do root
echo "📦 Instalando dependências do workspace..."
cd "$WORKSPACE_DIR"
python -m pip install --user -r requirements.txt

# 3. Validar importações críticas
echo "✅ Validando importações..."

# Verificar agent_framework versão e disponibilidade
python << 'EOF'
import sys
try:
    import agent_framework
    print(f"✅ agent_framework v{agent_framework.__version__ if hasattr(agent_framework, '__version__') else 'desconhecida'} instalado")

    from agent_framework import Agent, MCPStreamableHTTPTool
    print("✅ Agent disponível")
    print("✅ MCPStreamableHTTPTool disponível")

    from agent_framework.foundry import FoundryChatClient
    print("✅ FoundryChatClient disponível")

except ImportError as e:
    print(f"❌ Erro ao importar agent_framework: {e}")
    sys.exit(1)
EOF

# Validar agent.py pode ser importado (vai fazer o fallback se necessário)
echo "📋 Validando agent.py..."
python -c "
import sys
sys.path.insert(0, '$WORKSPACE_DIR/Ariba-Agent')
try:
    import agent
    print('✅ agent.py pode ser importado com sucesso')
except Exception as e:
    print(f'⚠️  Aviso ao importar agent.py: {e}')
" || true

# 4. Validar ferramentas de deploy
echo "🔍 Validando ferramentas de deploy..."
if command -v azd &> /dev/null; then
    echo "✅ Azure Developer CLI (azd) disponível: $(azd --version)"
else
    echo "⚠️  Azure Developer CLI (azd) não encontrado"
fi

if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI (gh) disponível: $(gh --version)"
else
    echo "⚠️  GitHub CLI (gh) não encontrado"
fi

# 5. Avisar sobre configuração .env
if [ ! -f "$WORKSPACE_DIR/Ariba-Agent/.env" ]; then
    echo "⚠️  Arquivo .env não encontrado em Ariba-Agent"
    echo "   Copie .env.example para .env e configure as variáveis"
fi

if [ ! -f "$WORKSPACE_DIR/Ariba-MCP/.env" ]; then
    echo "⚠️  Arquivo .env não encontrado em Ariba-MCP"
    echo "   Copie .env.example para .env se usar credenciais reais"
fi

echo ""
echo "✨ Setup concluído com sucesso!"
echo ""
echo "📚 Próximos passos para deploy no Azure:"
echo "   1. azd auth login              # Login no Azure"
echo "   2. azd up                      # Provisiona e deploya"
echo ""
echo "📚 Ou para desenvolvimento local:"
echo "   1. Terminal 1 - Ariba-MCP:   cd Ariba-MCP && python server.py"
echo "   2. Terminal 2 - Ariba-Agent: cd Ariba-Agent && python app.py"
