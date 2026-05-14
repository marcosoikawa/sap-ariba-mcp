"""
Thin HTTP client for the SAP Ariba Event Management API v2.

Docs: https://help.sap.com/docs/ariba-apis/event-management-api/event-management-api-v2-endpoints

Authentication uses OAuth2 client_credentials with:
  - ARIBA_APP_ID        (apiKey header)
  - ARIBA_CLIENT_ID     (OAuth client id)
  - ARIBA_CLIENT_SECRET (OAuth client secret)

If ARIBA_USE_MOCK=true (default when secrets missing), all calls return
local mock data so the server is fully usable out-of-the-box.
"""

from __future__ import annotations

import base64
import os
import time
from typing import Any

import httpx

from mock_data import EVENTS, PARTICIPANTS, BIDS


class AribaClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "ARIBA_BASE_URL",
            "https://openapi.ariba.com/api/sourcing-event-management/v2/prod",
        ).rstrip("/")
        self.oauth_url = os.getenv(
            "ARIBA_OAUTH_URL",
            "https://api.ariba.com/v2/oauth/token",
        )
        self.realm = os.getenv("ARIBA_REALM", "")
        self.app_id = os.getenv("ARIBA_APP_ID", "")
        self.client_id = os.getenv("ARIBA_CLIENT_ID", "")
        self.client_secret = os.getenv("ARIBA_CLIENT_SECRET", "")

        use_mock_env = os.getenv("ARIBA_USE_MOCK", "").strip().lower()
        if use_mock_env in ("true", "1", "yes"):
            self.use_mock = True
        elif use_mock_env in ("false", "0", "no"):
            self.use_mock = False
        else:
            # Auto: mock when no creds.
            self.use_mock = not (self.app_id and self.client_id and self.client_secret)

        self._token: str | None = None
        self._token_expiry: float = 0.0

    # ---------- auth ----------
    def _get_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 30:
            return self._token
        basic = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = httpx.post(
            self.oauth_url,
            headers=headers,
            data={"grant_type": "client_credentials"},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._token_expiry = time.time() + int(payload.get("expires_in", 3600))
        return self._token

    def _headers(self) -> dict[str, str]:
        return {
            "apiKey": self.app_id,
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        params = dict(params or {})
        if self.realm and "realm" not in params:
            params["realm"] = self.realm
        resp = httpx.get(url, headers=self._headers(), params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    # ---------- public API ----------
    def list_events(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.use_mock:
            data = EVENTS
            if status:
                data = [e for e in data if e["status"].lower() == status.lower()]
            return data[:limit]
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        data = self._get("/events", params=params)
        return data.get("events", data) if isinstance(data, dict) else data

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        if self.use_mock:
            return next((e for e in EVENTS if e["eventId"] == event_id), None)
        return self._get(f"/events/{event_id}")

    def list_participants(self, event_id: str) -> list[dict[str, Any]]:
        if self.use_mock:
            return PARTICIPANTS.get(event_id, [])
        data = self._get(f"/events/{event_id}/participants")
        return data.get("participants", data) if isinstance(data, dict) else data

    def list_bids(self, event_id: str) -> list[dict[str, Any]]:
        if self.use_mock:
            return BIDS.get(event_id, [])
        data = self._get(f"/events/{event_id}/bids")
        return data.get("bids", data) if isinstance(data, dict) else data
