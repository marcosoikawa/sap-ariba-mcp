"""Flask web UI for Ariba-Agent."""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

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
from agent import run_query  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ariba-agent-dev-secret")


@app.get("/")
def index():
    session.setdefault("thread_id", None)
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    thread_id = session.get("thread_id")
    try:
        reply = asyncio.run(run_query(message, thread_id=thread_id))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 500

    # Persiste o thread_id retornado para manter a conversa na mesma thread
    # (aparece agrupada em "My threads" no Foundry).
    session["thread_id"] = reply.thread_id
    return jsonify({"reply": reply.text, "thread_id": reply.thread_id})


@app.post("/api/reset")
def reset():
    session["thread_id"] = None
    return jsonify({"ok": True})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
