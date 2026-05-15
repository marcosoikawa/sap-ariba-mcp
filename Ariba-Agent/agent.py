"""
Ariba-Agent — exemplo didático de agente com Microsoft Agent Framework.

Fluxo em uma única função `run_query`:

    1) Cria a ferramenta MCP (conecta no servidor Ariba-MCP).
    2) Cria o client do modelo (Foundry / Azure AI).
    3) Monta o `Agent` com instruções + ferramenta.
    4) Roda a pergunta do usuário e devolve a resposta em texto.

Pré-requisitos:
    - `az login` (DefaultAzureCredential).
    - Variáveis no .env:
        ARIBA_MCP_URL                   (ex.: http://localhost:8000/mcp/)
        AZURE_AI_PROJECT_ENDPOINT       (endpoint do projeto Foundry)
        AZURE_AI_MODEL_DEPLOYMENT_NAME  (ex.: gpt-4o-mini)
"""

from __future__ import annotations

import os

from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent, MCPStreamableHTTPTool, Message
from agent_framework.foundry import FoundryChatClient


INSTRUCTIONS = """
Você é o Ariba Procurement Copilot, um assistente de compras especialista
em eventos de cotação no SAP Ariba (RFPs, RFIs e leilões reversos).

Como agir:
- Sempre use as ferramentas MCP para buscar dados antes de responder.
- Não invente eventIds, valores ou nomes de fornecedores.
- Mostre valores com a moeda do evento.
- Responda em português do Brasil, com bullets e tabelas quando ajudar.

Ferramentas disponíveis (via MCP):
- list_events(status?, limit?)        → lista eventos
- get_event(event_id)                 → detalhe de um evento
- list_participants(event_id)         → fornecedores do evento
- list_bids(event_id)                 → lances dos fornecedores
- event_summary(event_id)             → resumo + melhor lance por item
"""


async def run_query(
    user_message: str,
    history: list[dict] | None = None,
) -> str:
    """Envia uma pergunta ao agente e devolve a resposta em texto."""

    # 1) Ferramenta MCP — conecta o agente ao servidor Ariba-MCP.
    ferramenta_mcp = MCPStreamableHTTPTool(
        name="ariba-mcp",
        url=os.getenv("ARIBA_MCP_URL", "http://localhost:8000/mcp/"),
        description="Acesso ao SAP Ariba Event Management.",
    )

    # 2) Client do modelo — fala com o LLM no Azure AI Foundry.
    client = FoundryChatClient(
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        credential=DefaultAzureCredential(),  # usa `az login`
    )

    # 3) Abre a conexão MCP, monta o agente e roda a pergunta.
    async with ferramenta_mcp:
        agente = Agent(
            client=client,
            name="AribaProcurementCopilot",
            instructions=INSTRUCTIONS,
            tools=[ferramenta_mcp],
        )

        # Histórico (dicts) + pergunta atual → lista de Message.
        mensagens = [
            Message(role=t["role"], contents=[t["content"]])
            for t in (history or [])
            if t.get("role") and t.get("content")
        ]
        mensagens.append(Message(role="user", contents=[user_message]))

        resposta = await agente.run(mensagens)
        return resposta.text
