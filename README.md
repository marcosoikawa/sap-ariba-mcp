# SAP Ariba MCP

Workspace com dois projetos integrados: um **servidor MCP** que expõe a SAP Ariba Event Management API v2 e um **agente de procurement** que consome esse servidor via ferramentas MCP.

## 📦 Componentes

| Pasta | Descrição |
| ----- | --------- |
| [`Ariba-MCP/`](./Ariba-MCP)     | Servidor **MCP (Model Context Protocol)** em Python que expõe ferramentas para consultar SAP Ariba Event Management API v2. Pronto para deploy em **Azure Container Instances**. |
| [`Ariba-Agent/`](./Ariba-Agent) | Agente de **procurement** (Microsoft Agent Framework + Microsoft Foundry, `DefaultAzureCredential`) com **interface web Flask**, que consome o Ariba-MCP. |

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.12+
- Azure CLI (`az login` para Foundry)
- Docker (opcional)

### Terminal 1: Servidor MCP

```bash
cd Ariba-MCP
cp .env.example .env  # opcional: ajuste credenciais do Ariba
pip install -r requirements.txt
python server.py
# Acesso: http://localhost:8000/mcp/
```

### Terminal 2: Agente + UI

```bash
az login  # autentique no Azure

cd Ariba-Agent
cp .env.example .env  # configure AZURE_AI_PROJECT_ENDPOINT, etc.
pip install -r requirements.txt
python app.py
# Acesso: http://localhost:5000
```

## 📋 Configuração de Variáveis

### Ariba-MCP (.env)

```ini
# SAP Ariba (opcional - modo mock ativado sem credenciais)
ARIBA_APP_ID=
ARIBA_CLIENT_ID=
ARIBA_CLIENT_SECRET=

ARIBA_USE_MOCK=true  # usar dados mock para demo
HOST=0.0.0.0
PORT=8000
```

### Ariba-Agent (.env)

```ini
# MCP Server
ARIBA_MCP_URL=http://localhost:8000/mcp/

# Azure Foundry
AZURE_AI_PROJECT_ENDPOINT=https://<seu-recurso>.services.ai.azure.com/api/projects/<seu-projeto>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Flask
FLASK_SECRET=troque-isto
HOST=0.0.0.0
PORT=5000
```

## 🔧 Devcontainer

Abra no VS Code e selecione "Reopen in Container" para desenvolvimento automático com todas as dependências.

## 🐳 Docker

```bash
# Ariba-MCP
cd Ariba-MCP
docker build -t ariba-mcp:latest .
docker run --rm -p 8000:8000 --env-file .env ariba-mcp:latest

# Ariba-Agent
cd Ariba-Agent
docker build -t ariba-agent:latest .
docker run --rm -p 5000:5000 --env-file .env \
  -v $HOME/.azure:/root/.azure \
  ariba-agent:latest
```

## 📚 Ferramentas Disponíveis (MCP)

- **list_events** — Lista eventos (RFP / RFI / Auction)
- **get_event** — Detalhe de um evento
- **list_participants** — Fornecedores (convidados/participantes/recusados)
- **list_bids** — Lances dos fornecedores
- **event_summary** — Resumo com melhor lance por item

## 🤖 Exemplo de Uso

Na UI (http://localhost:5000), digite:

```
Liste os eventos abertos no Ariba
```

O agente irá:
1. Chamar `list_events` do Ariba-MCP
2. Processar com o modelo Foundry
3. Retornar formatado em português

## ☁️ Deploy em Azure

### Ariba-MCP em Container Instances

```bash
cd Ariba-MCP

RG=rg-ariba-mcp
LOC=brazilsouth
ACR=aribamcpacr$RANDOM

az group create -n $RG -l $LOC
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true
az acr build -r $ACR -t ariba-mcp:latest .

ACR_USER=$(az acr credential show -n $ACR --query username -o tsv)
ACR_PASS=$(az acr credential show -n $ACR --query passwords[0].value -o tsv)
ACR_SERVER=$(az acr show -n $ACR --query loginServer -o tsv)

az container create \
  -g $RG -n ariba-mcp \
  --image $ACR_SERVER/ariba-mcp:latest \
  --registry-login-server $ACR_SERVER \
  --registry-username $ACR_USER \
  --registry-password $ACR_PASS \
  --ports 8000 \
  --dns-name-label ariba-mcp-$RANDOM \
  --environment-variables ARIBA_USE_MOCK=true
```

## 📖 Documentação Adicional

- [Ariba-MCP](./Ariba-MCP/README.md) — Detalhes do servidor MCP
- [Ariba-Agent](./Ariba-Agent/README.md) — Detalhes do agente
- [SAP Ariba Event Management API](https://help.sap.com/docs/ariba-apis/event-management-api/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/)

## 🆘 Troubleshooting

| Erro | Solução |
| ---- | --------- |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `DefaultAzureCredential` não funciona | `az login` e configure credenciais |
| Ariba-MCP retorna 401 | Verifique credenciais SAP Ariba em `.env` |
| Agent não encontra ferramentas | Confirme `ARIBA_MCP_URL` está acessível |

## 📝 Licença

MIT License - veja LICENSE para detalhes.
