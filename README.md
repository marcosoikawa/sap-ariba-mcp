
# SAP Ariba MCP & Agent

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SEU-REPO-AQUI)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/SEU-REPO-AQUI)

<div align="center">
  
[**Features**](#features) \| [**Getting Started**](#getting-started) \| [**Deploying**](#deploying) \| [**Testing the Agent**](#testing-the-agent) \| [**Guidance**](#guidance) \| [**Resources**](#resources) \| [**Licença**](#licença)

</div>

---

## Features

Solução completa para integração com SAP Ariba Event Management API v2, composta por:

- **Servidor MCP**: expõe ferramentas MCP para consulta de eventos SAP Ariba.
- **Agente de Procurement**: interface web (Flask) e integração com Microsoft Agent Framework/Foundry.
- **Deploy automatizado no Azure** via Azure Developer CLI (`azd`).
- **Ambiente pronto para Codespaces e Dev Containers**.
- **APIs e UI** para consulta, simulação e integração.

### Principais Funcionalidades
- Consulta de eventos, participantes e lances do Ariba.
- Resumo de eventos e melhores lances.
- Modo mock para testes sem credenciais SAP.
- Pronto para produção em Azure Container Apps.

---

## Getting Started

### Pré-requisitos

- [Azure CLI](https://learn.microsoft.com/cli/azure/what-is-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
- [Python 3.12+](https://www.python.org/about/gettingstarted/)
- [Docker](https://www.docker.com/get-started/) (opcional, para Dev Containers)

### Opções de Deployment

Escolha uma das opções abaixo para preparar o ambiente. Em seguida, siga para a seção [Deploying](#deploying) para subir tudo no Azure.

<details>
<summary><b>Deploy no GitHub Codespaces</b></summary>

### GitHub Codespaces

Você pode executar este projeto usando o **GitHub Codespaces**. O botão abaixo abre uma instância web do VS Code no seu navegador, já com todas as dependências instaladas via Devcontainer:

1. Abra o projeto no Codespaces (pode levar alguns minutos na primeira vez):

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SEU-REPO-AQUI)

2. Aceite os valores padrão na página de criação do Codespaces.
3. Aguarde o Devcontainer terminar o setup (instala automaticamente `requirements.txt` da raiz).
4. Abra um terminal (caso ainda não esteja aberto).
5. Faça login no Azure: `az login` e `azd auth login`.
6. Continue com os [passos de deploy](#deploying).

</details>

<details>
<summary><b>Deploy no VS Code Dev Containers</b></summary>

### VS Code Dev Containers

Execute o projeto localmente em um Dev Container, usando o VS Code + Docker Desktop + a extensão [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Inicie o Docker Desktop (instale-o, caso ainda não tenha).
2. Abra o projeto no Dev Container:

   [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/SEU-REPO-AQUI)

   Ou, com o repositório já clonado, abra a pasta no VS Code e selecione **"Reopen in Container"**.
3. Aguarde o Devcontainer subir e instalar as dependências (`requirements.txt` da raiz).
4. Abra um terminal no VS Code.
5. Faça login no Azure: `az login` e `azd auth login`.
6. Continue com os [passos de deploy](#deploying).

</details>

<details>
<summary><b>Deploy no seu ambiente local</b></summary>

### Ambiente Local

Se preferir não usar Codespaces nem Dev Containers, você pode preparar o ambiente manualmente:

1. Verifique se as seguintes ferramentas estão instaladas:
   - `bash`
   - [Azure CLI](https://learn.microsoft.com/cli/azure/what-is-azure-cli) (`az`)
   - [Azure Developer CLI](https://aka.ms/install-azd) (`azd`)
   - [Python 3.12+](https://www.python.org/about/gettingstarted/) (`python`)
   - [Docker](https://www.docker.com/get-started/) (opcional, para builds locais)

2. Clone o projeto **ou** baixe direto com `azd`:

   ```bash
   azd init -t SEU-REPO-AQUI
   ```

   > **Nota:** o comando acima deve ser executado em uma nova pasta. Você não precisa rodar `git clone` — o `azd init` cuida disso.

3. Abra a pasta do projeto no terminal ou editor de sua preferência.

4. Instale as dependências Python (uma única vez, na raiz):

   ```bash
   pip install -r requirements.txt
   ```

5. Continue com os [passos de deploy](#deploying).

</details>

### Deploying

Uma vez aberto o projeto no [Codespaces](#github-codespaces), no [Dev Containers](#vs-code-dev-containers) ou [localmente](#ambiente-local), você pode implantar o ambiente no Azure seguindo os passos abaixo:

> [!IMPORTANT]
> Execute os comandos `azd` a partir da raiz do repositório, onde está o arquivo `azure.yaml`.

1. **Login no Azure e no Azure Developer CLI:**

   ```bash
   az login
   az account show
   azd auth login
   ```

   Se você tiver múltiplas subscriptions, selecione a desejada antes do deploy:

   ```bash
   az account set --subscription "<subscription-id-ou-nome>"
   ```

2. **Provisione e implante todos os recursos:**

   ```bash
   azd up
   ```

   O `azd` irá pedir:
   - Um **nome de ambiente** (ex.: `ariba-mcp-dev`)
   - A **subscription** Azure a usar
   - A **região** (recomendado: `brazilsouth`, `eastus2` ou `swedencentral`)

   Em seguida, ele provisiona os recursos definidos em `infra/main.bicep` (Container Registry, Container Apps Environment, Container Apps para `Ariba-MCP` e `Ariba-Agent`) e faz o deploy do código.

3. **Configure variáveis sensíveis (opcional, antes do `azd up`):**

   ```bash
   # Credenciais SAP Ariba (sem isso, o MCP roda em modo mock)
   azd env set ARIBA_APP_ID <seu-app-id>
   azd env set ARIBA_CLIENT_ID <seu-client-id>
   azd env set ARIBA_CLIENT_SECRET <seu-client-secret>
   azd env set ARIBA_USE_MOCK false

   # Endpoint do Azure AI Foundry para o agente
   azd env set AZURE_AI_PROJECT_ENDPOINT https://<seu-recurso>.services.ai.azure.com/api/projects/<seu-projeto>
   azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME gpt-4o-mini
   ```

4. **Ao final do `azd up`**, os endpoints das duas Container Apps serão exibidos no terminal:

   - **Ariba-MCP** → `https://ariba-mcp.<region>.azurecontainerapps.io/mcp/`
   - **Ariba-Agent** → `https://ariba-agent.<region>.azurecontainerapps.io`

   Acesse a URL do Agent no navegador para começar a usar a UI.

5. **Para atualizar somente o código** (sem reprovisionar infraestrutura):

   ```bash
   azd deploy
   ```

6. **Para reprovisionar somente a infraestrutura:**

   ```bash
   azd provision
   ```

> [!NOTE]
> Se ocorrer um erro de disponibilidade de recurso em uma região, refaça o `azd up` escolhendo outra região. Para mudar de região depois do primeiro deploy, remova a pasta `.azure/` antes de rodar `azd up` novamente.

---

## Testing the Agent

Após o deploy, acesse a URL do Container App retornada pelo `azd up`.

### Teste via UI Web
1. Abra o navegador na URL do agente (porta 5000).
2. Utilize a interface para consultar eventos, participantes e lances.

### Teste via API MCP
1. Acesse a URL do MCP (porta 8000).
2. Utilize ferramentas como Postman ou curl para testar os endpoints.

---

## Guidance

### Limpeza de Recursos
Para remover todos os recursos criados no Azure:
```bash
azd down
```

### Customização
- Edite variáveis em `.env` para ajustar integrações e credenciais.
- Modifique os arquivos em `infra/` para personalizar a infraestrutura.

---

## Resources

- [SAP Ariba Event Management API](https://help.sap.com/docs/ariba-apis/event-management-api/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Documentação Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
- [Documentação Container Apps](https://learn.microsoft.com/azure/container-apps/)

---

## Licença

MIT License - veja LICENSE para detalhes.
