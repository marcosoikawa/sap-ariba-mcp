# Ariba-Agent

Agente de **procurement** especializado em eventos do SAP Ariba (RFPs,
leilões reversos, RFIs), construído com:

- **Microsoft Agent Framework** (`agent-framework`)
- **Microsoft Foundry Agents** (`AzureAIAgentClient`) com
  `DefaultAzureCredential` — sem API key. Faça `az login` antes.
- **MCP Streamable HTTP** apontando para o servidor [Ariba-MCP](../Ariba-MCP).
- **Flask** como interface web.

## Capacidades

O agente consome o Ariba-MCP e responde perguntas como:

- "Quais eventos estão abertos no Ariba?"
- "Resuma o evento Doc2233445566."
- "Quem recusou a cotação de matérias-primas químicas?"
- "Qual o melhor lance por item no leilão de logística Sudeste?"
- "Liste os fornecedores que participaram do RFI de embalagem sustentável."

## Configuração

1. Faça login no Azure:
   ```bash
   az login
   ```
2. Copie `.env.example` para `.env` e preencha:
   - `ARIBA_MCP_URL` — URL pública do Ariba-MCP (ex.: ACI no Azure).
   - `AZURE_AI_PROJECT_ENDPOINT` — endpoint do seu projeto Foundry.
   - `AZURE_AI_MODEL_DEPLOYMENT_NAME` — ex.: `gpt-4o-mini`.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
# UI:  http://localhost:5000
```

## Devcontainer

Abra a pasta no VS Code → "Reopen in Container".

## Docker

```bash
docker build -t ariba-agent:latest .
docker run --rm -p 5000:5000 --env-file .env \
  -v $HOME/.azure:/root/.azure \
  ariba-agent:latest
```

> O mount de `~/.azure` permite que `DefaultAzureCredential` use o token
> do `az login` do host. Em produção (Container Apps / ACI) prefira
> Managed Identity.

## Arquitetura

```
[ Usuário ] ──► Flask (UI)
                 │
                 ▼
        ChatAgent (Agent Framework)
                 │
        AzureAIAgentClient ──► Microsoft Foundry (modelo)
                 │
        MCPStreamableHTTPTool
                 │
                 ▼
        Ariba-MCP  ──►  SAP Ariba Event Management API v2
```
