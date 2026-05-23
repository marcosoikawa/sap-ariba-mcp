"""
Ariba-MCP — MCP server (Streamable HTTP) exposing tools that query
the SAP Ariba Event Management API v2.

Run locally:
    python server.py

Endpoint (default):
    http://localhost:8000/mcp/
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from ariba_client import AribaClient

load_dotenv()

mcp = FastMCP(
    name="Ariba-MCP",
    instructions=(
        "Servidor MCP para o SAP Ariba Event Management. "
        "Use as ferramentas para listar eventos de sourcing, ver participantes, "
        "lances de fornecedores, datas e status de cotações."
    ),
)

client = AribaClient()


@mcp.tool
def list_events(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Lista eventos do Ariba (RFP / RFI / Auction).

    Args:
        status: Filtro opcional (ex.: "Open", "Closed").
        limit:  Número máximo de eventos a retornar.
    """
    return client.list_events(status=status, limit=limit)


@mcp.tool
def get_event(event_id: str) -> dict[str, Any] | None:
    """Detalhe de um evento (datas, dono, moeda, contagens).

    Args:
        event_id: ID do evento (ex.: "Doc1234567890").
    """
    return client.get_event(event_id)


@mcp.tool
def list_participants(event_id: str) -> list[dict[str, Any]]:
    """Fornecedores convidados ao evento, incluindo quem participou,
    recusou (Declined) ou não respondeu (NoResponse)."""
    return client.list_participants(event_id)


@mcp.tool
def list_bids(event_id: str) -> list[dict[str, Any]]:
    """Lances submetidos por fornecedores no evento (item, valor, moeda, data)."""
    return client.list_bids(event_id)


@mcp.tool
def event_summary(event_id: str) -> dict[str, Any]:
    """Resumo consolidado: evento + contagem de participantes/recusas +
    melhor lance por item de linha."""
    event = client.get_event(event_id)
    if not event:
        return {"error": f"Evento {event_id} não encontrado."}

    participants = client.list_participants(event_id)
    bids = client.list_bids(event_id)

    participated = [p for p in participants if p.get("status") == "Participated"]
    declined = [p for p in participants if p.get("status") == "Declined"]
    no_response = [p for p in participants if p.get("status") == "NoResponse"]

    best_by_item: dict[str, dict[str, Any]] = {}
    for b in bids:
        item = b.get("lineItem", "n/a")
        if item not in best_by_item or b["amount"] < best_by_item[item]["amount"]:
            best_by_item[item] = b

    return {
        "event": event,
        "counts": {
            "invited": len(participants),
            "participated": len(participated),
            "declined": len(declined),
            "noResponse": len(no_response),
            "totalBids": len(bids),
        },
        "participantsParticipated": participated,
        "participantsDeclined": declined,
        "bestBidPerLineItem": list(best_by_item.values()),
    }


@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok", "mock": client.use_mock})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    # Streamable HTTP transport → exposes URL at http://host:port/mcp
    mcp.run(transport="http", host=host, port=port, path="/mcp", stateless_http=True)
