"""Flask web UI for Ariba-Agent."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

from agent import run_query

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ariba-agent-dev-secret")


@app.get("/")
def index():
    session.setdefault("history", [])
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    history = session.get("history", [])
    try:
        reply = asyncio.run(run_query(message, history=history))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 500

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    session["history"] = history[-20:]  # cap history
    return jsonify({"reply": reply})


@app.post("/api/reset")
def reset():
    session["history"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
