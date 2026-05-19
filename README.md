
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

> [!NOTE]
> Este projeto esta configurado com `remoteBuild: true` no `azure.yaml` para os servicos de Container Apps.
> Isso permite executar `azd up` sem Docker local, pois o build de imagem e feito remotamente no Azure Container Registry (ACR).
> Cada serviço usa seu próprio arquivo de dependências Python:
> - `Ariba-Agent/requirements.txt`
> - `Ariba-MCP/requirements.txt`

### Opções de Deployment

Escolha uma das opções abaixo para preparar o ambiente. Em seguida, siga para a seção [Deploying](#deploying) para subir tudo no Azure.

<details>
<summary><b>Deploy no GitHub Codespaces</b></summary>

### GitHub Codespaces

Você pode executar este projeto usando o **GitHub Codespaces**. O botão abaixo abre uma instância web do VS Code no seu navegador, já com todas as dependências instaladas via Devcontainer:

1. Abra o projeto no Codespaces (pode levar alguns minutos na primeira vez):

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SEU-REPO-AQUI)

2. Aceite os valores padrão na página de criação do Codespaces.
3. Aguarde o Devcontainer terminar o setup.
4. Instale as dependências dos serviços:

   ```bash
   pip install -r Ariba-Agent/requirements.txt
   pip install -r Ariba-MCP/requirements.txt
   ```
5. Abra um terminal (caso ainda não esteja aberto).
6. Faça login no Azure: `az login` e `azd auth login`.
7. Continue com os [passos de deploy](#deploying).

</details>

<details>
<summary><b>Deploy no VS Code Dev Containers</b></summary>

### VS Code Dev Containers

Execute o projeto localmente em um Dev Container, usando o VS Code + Docker Desktop + a extensão [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Inicie o Docker Desktop (instale-o, caso ainda não tenha).
2. Abra o projeto no Dev Container:

   [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/SEU-REPO-AQUI)

   Ou, com o repositório já clonado, abra a pasta no VS Code e selecione **"Reopen in Container"**.
3. Aguarde o Devcontainer subir.
4. Instale as dependências dos serviços:

   ```bash
   pip install -r Ariba-Agent/requirements.txt
   pip install -r Ariba-MCP/requirements.txt
   ```

5. Abra um terminal no VS Code.
6. Faça login no Azure: `az login` e `azd auth login`.
7. Continue com os [passos de deploy](#deploying).

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

4. Instale as dependências Python dos serviços:

   ```bash
   pip install -r Ariba-Agent/requirements.txt
   pip install -r Ariba-MCP/requirements.txt
   ```

5. Continue com os [passos de deploy](#deploying).

</details>

### Validação da Infraestrutura

Antes de fazer deploy, você pode validar que a infraestrutura Bicep está sintaticamente correta:

```bash
cd infra/
bicep build main.bicep
```

Se o comando for bem-sucedido, um arquivo `main.json` será gerado (Template ARM compilada).

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

## Security Considerations

ACS atualmente não oferece suporte a Managed Identity para este fluxo. Quando necessário, segredos de conexão devem ser armazenados no Key Vault e injetados no Container App por referência de segredo.

---

## Additional Disclaimers

To the extent that the Software includes components or code used in or derived from Microsoft products or services, including without limitation Microsoft Azure Services (collectively, "Microsoft Products and Services"), you must also comply with the Product Terms applicable to such Microsoft Products and Services. You acknowledge and agree that the license governing the Software does not grant you a license or other right to use Microsoft Products and Services. Nothing in the license or this ReadMe file will serve to supersede, amend, terminate or modify any terms in the Product Terms for any Microsoft Products and Services.

You must also comply with all domestic and international export laws and regulations that apply to the Software, which include restrictions on destinations, end users, and end use. For further information on export restrictions, visit https://aka.ms/exporting.

You acknowledge that the Software and Microsoft Products and Services (1) are not designed, intended or made available as a medical device(s), and (2) are not designed or intended to be a substitute for professional medical advice, diagnosis, treatment, or judgment and should not be used to replace or as a substitute for professional medical advice, diagnosis, treatment, or judgment. Customer is solely responsible for displaying and/or obtaining appropriate consents, warnings, disclaimers, and acknowledgements to end users of Customer's implementation of the Online Services.

You acknowledge the Software is not subject to SOC 1 and SOC 2 compliance audits. No Microsoft technology, nor any of its component technologies, including the Software, is intended or made available as a substitute for the professional advice, opinion, or judgment of a certified financial services professional. Do not use the Software to replace, substitute, or provide professional financial advice or judgment.

BY ACCESSING OR USING THE SOFTWARE, YOU ACKNOWLEDGE THAT THE SOFTWARE IS NOT DESIGNED OR INTENDED TO SUPPORT ANY USE IN WHICH A SERVICE INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE COULD RESULT IN THE DEATH OR SERIOUS BODILY INJURY OF ANY PERSON OR IN PHYSICAL OR ENVIRONMENTAL DAMAGE (COLLECTIVELY, "HIGH-RISK USE"), AND THAT YOU WILL ENSURE THAT, IN THE EVENT OF ANY INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE, THE SAFETY OF PEOPLE, PROPERTY, AND THE ENVIRONMENT ARE NOT REDUCED BELOW A LEVEL THAT IS REASONABLY, APPROPRIATE, AND LEGAL, WHETHER IN GENERAL OR IN A SPECIFIC INDUSTRY. BY ACCESSING THE SOFTWARE, YOU FURTHER ACKNOWLEDGE THAT YOUR HIGH-RISK USE OF THE SOFTWARE IS AT YOUR OWN RISK.

---

## Trademarks:

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party policies.

---

## Data Collection:

The software may collect information about you and your use of the software and send it to Microsoft. Microsoft may use this information to provide services and improve our products and services. You may turn off the telemetry as described in the repository. There are also some features in the software that may enable you and Microsoft to collect data from users of your applications. If you use these features, you must comply with applicable law, including providing appropriate notices to users of your applications together with a copy of Microsoft's privacy statement. Our privacy statement is located [here](https://go.microsoft.com/fwlink/?LinkID=824704). You can learn more about data collection and use in the help documentation and our privacy statement. Your use of the software operates as your consent to these practices.

Note:
- No telemetry or data collection is directly added in this accelerator project.
- Review telemetry behavior for each Azure service API used by this solution.

---

## Licença

MIT License - veja LICENSE para detalhes.
