"""
Ariba-Agent - agente de procurement especializado em eventos do SAP Ariba.

Usa Microsoft Agent Framework + Microsoft Foundry Agents com
autenticacao padrao (DefaultAzureCredential - `az login`).
Consome o Ariba-MCP via Streamable HTTP.
"""

from __future__ import annotations

import os

from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent, MCPStreamableHTTPTool, Message
from agent_framework.foundry import FoundryChatClient


SYSTEM_PROMPT = """Voce e o Ariba Procurement Copilot, um agente
especialista em sourcing e gestao de eventos de cotacao no SAP Ariba.

Responsabilidades:
- Auxiliar compradores a explorar eventos de RFP, RFI e leiloes reversos.
- Buscar e resumir lances de fornecedores, datas de abertura/encerramento,
  participantes, recusas e melhor proposta por item.
- Sempre que possivel, use as ferramentas MCP conectadas ao Ariba para
  obter dados frescos antes de responder. Nao invente eventIds, valores
  ou nomes de fornecedores.
- Apresente valores monetarios com a moeda do evento.
- Quando o usuario pedir um resumo de um evento, prefira a ferramenta
  event_summary.
- Quando o usuario nao souber o eventId, comece por list_events.
- Responda em portugues do Brasil, de forma objetiva, com bullets e
  tabelas markdown quando ajudar.

Ferramentas disponiveis (via MCP):
- list_events(status?, limit?)
- get_event(event_id)
- list_participants(event_id)
- list_bids(event_id)
- event_summary(event_id)
"""


def build_mcp_tool() -> MCPStreamableHTTPTool:
    url = os.getenv("ARIBA_MCP_URL", "http://localhost:8000/mcp/")
    return MCPStreamableHTTPTool(
        name="ariba-mcp",
        url=url,
        description="Acesso ao SAP Ariba Event Management via MCP.",
    )


def build_agent_client() -> FoundryChatClient:
    """Cria o client do Foundry usando DefaultAzureCredential."""
    credential = DefaultAzureCredential()
    return FoundryChatClient(
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        credential=credential,
    )


async def run_query(user_message: str, history: list[dict] | None = None) -> str:
    """Executa uma rodada do agente e retorna a resposta como texto."""
    mcp_tool = build_mcp_tool()
    client = build_agent_client()

    async with mcp_tool:
        agent = Agent(
            client=client,
            name="AribaProcurementCopilot",
            instructions=SYSTEM_PROMPT,
            tools=[mcp_tool],
        )

        messages: list[Message] = []
        for turn in history or []:
            role = turn.get("role")
            content = turn.get("content", "")
            if role and content:
                messages.append(Message(role=role, contents=[content]))
        messages.append(Message(role="user", contents=[user_message]))

        result = await agent.run(messages)
        return result.text