"""Ariba-Agent — Microsoft Agent Framework + Foundry."""

from __future__ import annotations

import os
from typing import Any, AsyncIterator

from agent_framework import MCPStreamableHTTPTool
from agent_framework.foundry import FoundryAgent
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import AzureCliCredential

_SESSIONS: dict[str, Any] = {}


def _ensure_agent_version(endpoint: str, name: str, model: str) -> str:
    client = AIProjectClient(endpoint=endpoint, credential=AzureCliCredential())
    try:
        versions = list(client.agents.list_versions(agent_name=name, limit=50))
    except ResourceNotFoundError:
        versions = []
    if versions:
        return str(max(versions, key=lambda v: int(str(v.version)) if str(v.version).isdigit() else 0).version)
    created = client.agents.create_version(
        agent_name=name,
        definition=PromptAgentDefinition(
            kind="prompt",
            model=model,
            instructions="Você é um agente de procurement SAP Ariba.",
        ),
    )
    return str(created.version)


def _build_agent() -> tuple[FoundryAgent, MCPStreamableHTTPTool]:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    name = os.environ["AZURE_AI_AGENT_NAME"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    version = os.getenv("AZURE_AI_AGENT_VERSION") or _ensure_agent_version(endpoint, name, model)

    mcp = MCPStreamableHTTPTool(
        name="ariba-mcp",
        url=os.getenv("ARIBA_MCP_URL", "http://localhost:8000/mcp"),
        description="Acesso ao SAP Ariba Event Management.",
    )
    agent = FoundryAgent(
        project_endpoint=endpoint,
        agent_name=name,
        agent_version=version,
        credential=AzureCliCredential(),
        tools=[mcp],
    )
    return agent, mcp


def _get_session(agent: FoundryAgent, session_id: str) -> Any:
    session = _SESSIONS.get(session_id)
    if session is None:
        session = agent.create_session()
        _SESSIONS[session_id] = session
    return session


async def run_query_stream(user_message: str, session_id: str) -> AsyncIterator[str]:
    agent, mcp = _build_agent()
    session = _get_session(agent, session_id)
    async with mcp:
        async for update in agent.run(user_message, stream=True, session=session):
            if getattr(update, "text", None):
                yield update.text


def reset_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)
