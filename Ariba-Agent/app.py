"""Flask web UI for Ariba-Agent."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import threading
import uuid

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, session

load_dotenv()

# ============================================================================
# Telemetria (OpenTelemetry -> Application Insights -> Foundry Monitoring)
# ----------------------------------------------------------------------------
# - `configure_azure_monitor` instala exporters OTel (traces, logs, metrics)
#   apontando para o App Insights cuja connection string vem da env var
#   APPLICATIONINSIGHTS_CONNECTION_STRING.
# - `setup_observability` do Agent Framework ativa os spans `gen_ai.*`
#   (chamadas LLM, tool calls, agent runs) — eles é que populam a aba
#   "Tracing" do Foundry no portal ai.azure.com.
# - `FlaskInstrumentor` adiciona spans automáticos para requests HTTP.
# ============================================================================
_APPINSIGHTS_CONN = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
if _APPINSIGHTS_CONN:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=_APPINSIGHTS_CONN,
            logger_name="ariba_agent",
        )

        from agent_framework.observability import setup_observability

        setup_observability(
            enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "false").lower() == "true",
        )

        from opentelemetry.instrumentation.flask import FlaskInstrumentor

        FlaskInstrumentor().instrument()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Telemetry setup failed: %s", exc)
else:
    logging.getLogger(__name__).info(
        "APPLICATIONINSIGHTS_CONNECTION_STRING não definida — telemetria desabilitada."
    )

# Import depois do setup p/ garantir que o Agent Framework já vê a config OTel.
from agent import reset_session, run_query_stream  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ariba-agent-dev-secret")


@app.get("/")
def index():
    session.setdefault("sid", uuid.uuid4().hex)
    return render_template("index.html")


def _sse(message: str, sid: str):
    """Bridge async generator -> sync iterator emitindo eventos SSE."""
    q: queue.Queue = queue.Queue()
    SENTINEL = object()

    def runner():
        async def consume():
            async for chunk in run_query_stream(message, session_id=sid):
                q.put(("chunk", chunk))

        try:
            asyncio.run(consume())
        except Exception as exc:  # noqa: BLE001
            q.put(("error", f"{type(exc).__name__}: {exc}"))
        finally:
            q.put(SENTINEL)

    threading.Thread(target=runner, daemon=True).start()

    while True:
        item = q.get()
        if item is SENTINEL:
            yield "event: done\ndata: {}\n\n"
            return
        kind, payload = item
        yield f"event: {kind}\ndata: {json.dumps({'text': payload})}\n\n"


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    sid = session.setdefault("sid", uuid.uuid4().hex)
    return Response(
        _sse(message, sid),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/reset")
def reset():
    sid = session.get("sid")
    if sid:
        reset_session(sid)
    session["sid"] = uuid.uuid4().hex
    return jsonify({"ok": True})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
