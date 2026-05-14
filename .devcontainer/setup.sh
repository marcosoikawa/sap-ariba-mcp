#!/bin/bash
set -e

echo "🔧 Configurando ambiente sap-ariba-mcp..."

WORKSPACE_DIR="/workspaces/sap-ariba-mcp"

# 1. Instalar dependências do root
echo "📦 Instalando dependências do workspace..."
python -m pip install --user -r requirements.txt

# 2. Instalar dependências específicas de cada subprojeto
echo "📦 Instalando dependências Ariba-MCP..."
cd "$WORKSPACE_DIR/Ariba-MCP"
python -m pip install --user -r requirements.txt

echo "📦 Instalando dependências Ariba-Agent..."
cd "$WORKSPACE_DIR/Ariba-Agent"
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
    print(f'❌ Erro ao importar agent.py: {e}')
    sys.exit(1)
" || exit 1

# 4. Avisar sobre configuração .env
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
echo "📚 Próximos passos:"
echo "   1. Ariba-MCP:   cd Ariba-MCP && python server.py"
echo "   2. Ariba-Agent: cd Ariba-Agent && python app.py"
