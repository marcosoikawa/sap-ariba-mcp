# Ariba-MCP

Servidor **MCP (Model Context Protocol)** em Python que expõe ferramentas
para consultar a API **SAP Ariba Event Management v2**
(<https://help.sap.com/docs/ariba-apis/event-management-api/event-management-api-v2-endpoints>).

Permite consultar:

- Lista de eventos de sourcing (RFP / RFI / Auction).
- Datas de início e fim, status, dono, moeda.
- Fornecedores convidados / participantes / recusados.
- Lances submetidos (item, valor, moeda, data).
- Resumo consolidado com melhor lance por linha.

A autenticação usa **App ID + Client ID + Client Secret** (OAuth2
`client_credentials`). Sem credenciais, o servidor responde com **dados
mock** prontos para demonstração.

## Ferramentas MCP expostas

| Tool                  | Descrição                                              |
| --------------------- | ------------------------------------------------------ |
| `list_events`         | Lista eventos (filtro opcional por status)             |
| `get_event`           | Detalhe de um evento                                   |
| `list_participants`   | Fornecedores convidados / quem participou / recusou    |
| `list_bids`           | Lances dos fornecedores                                |
| `event_summary`       | Resumo consolidado (counts + melhor lance por item)    |

## URL exposta

Após `python server.py` o endpoint MCP fica em:

```
http://localhost:8000/mcp/
```

Health check: `GET http://localhost:8000/health`.

## Rodar localmente

```bash
cp .env.example .env       # ajuste se tiver credenciais reais
pip install -r requirements.txt
python server.py
```

## Rodar via devcontainer

Abra a pasta no VS Code → "Reopen in Container".

## Build Docker

```bash
docker build -t ariba-mcp:latest .
docker run --rm -p 8000:8000 --env-file .env ariba-mcp:latest
```

## Deploy em Azure Container Instances

```bash
# Variáveis
RG=rg-ariba-mcp
LOC=brazilsouth
ACR=aribamcpacr$RANDOM
ACI=ariba-mcp
DNS=ariba-mcp-$RANDOM

# 1. Resource group + ACR
az group create -n $RG -l $LOC
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true

# 2. Build da imagem direto no ACR
az acr build -r $ACR -t ariba-mcp:latest .

# 3. Credenciais do ACR
ACR_USER=$(az acr credential show -n $ACR --query username -o tsv)
ACR_PASS=$(az acr credential show -n $ACR --query passwords[0].value -o tsv)
ACR_SERVER=$(az acr show -n $ACR --query loginServer -o tsv)

# 4. Container Instance com DNS publico
az container create \
  -g $RG -n $ACI \
  --image $ACR_SERVER/ariba-mcp:latest \
  --registry-login-server $ACR_SERVER \
  --registry-username $ACR_USER \
  --registry-password $ACR_PASS \
  --ports 8000 \
  --dns-name-label $DNS \
  --location $LOC \
  --environment-variables \
      ARIBA_USE_MOCK=true \
      HOST=0.0.0.0 PORT=8000

# 5. URL publica do MCP
echo "MCP URL: http://${DNS}.${LOC}.azurecontainer.io:8000/mcp/"
```

Para usar credenciais reais, passe-as como `--secure-environment-variables`:

```bash
--secure-environment-variables \
    ARIBA_APP_ID=... ARIBA_CLIENT_ID=... ARIBA_CLIENT_SECRET=... \
    ARIBA_REALM=... ARIBA_USE_MOCK=false
```
