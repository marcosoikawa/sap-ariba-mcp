#!/bin/bash
set -e

echo "🔧 Inicializando repositório Git..."

# Configurar git (se necessário)
if ! git config user.email >/dev/null 2>&1; then
    echo "📝 Configurando Git..."
    git config --global user.email "your-email@example.com"
    git config --global user.name "Your Name"
    echo "   ⚠️  Configure user.email e user.name globais:"
    echo "   git config --global user.email 'seu-email@example.com'"
    echo "   git config --global user.name 'Seu Nome'"
fi

# Inicializar repositório (se não existir)
if [ ! -d .git ]; then
    echo "📦 Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Initial commit: SAP Ariba MCP workspace

- Servidor MCP (Ariba-MCP) com ferramentas para Event Management API v2
- Agente de procurement (Ariba-Agent) com Agent Framework + Foundry
- Devcontainer para desenvolvimento
- Docker e docker-compose para deploy"
    echo "✅ Repositório inicializado com commit inicial"
else
    echo "✅ Repositório Git já existe"
    git status
fi

echo ""
echo "📚 Próximos passos:"
echo ""
echo "1. Criar repositório vazio no GitHub (sem README, .gitignore, LICENSE)"
echo ""
echo "2. Adicionar remote:"
echo "   git remote add origin https://github.com/SEU_USUARIO/sap-ariba-mcp.git"
echo ""
echo "3. Fazer push da branch main:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "✨ Pronto para enviar ao GitHub!"
