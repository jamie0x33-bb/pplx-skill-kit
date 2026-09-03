"""Thin client over the connector service.

Routes are the ones the sandbox tooling uses:

    GET  {base}/rest/connector-service/connectors
    POST {base}/rest/connector-service/connectors/{source_id}/describe
    POST {base}/rest/connector-service/connectors/{source_id}/tools/{tool}/execute
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .config import ConnectorConfig, load

TIMEOUT = int(os.environ.get("SKILL_KIT_TIMEOUT", "60"))


class ConnectorError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"connector service returned {status}")
        self.status = status
        self.body = body


def _request(cfg: ConnectorConfig, method: str, path: str, payload: dict | None = None):
    url = f"{cfg.base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=cfg.headers())
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:  # surface the service's own message
        raise ConnectorError(exc.code, exc.read().decode(errors="replace")) from None


def list_connectors(cfg: ConnectorConfig | None = None) -> list[dict]:
    cfg = cfg or load()
    return _request(cfg, "GET", "/rest/connector-service/connectors").get("connectors", [])


def connected(cfg: ConnectorConfig | None = None) -> list[dict]:
    return [c for c in list_connectors(cfg) if c.get("status") == "CONNECTED"]


def describe(source_id: str, cfg: ConnectorConfig | None = None) -> dict:
    cfg = cfg or load()
    return _request(cfg, "POST", f"/rest/connector-service/connectors/{source_id}/describe", {})


def call_tool(source_id: str, tool_name: str, arguments: dict, cfg: ConnectorConfig | None = None) -> dict:
    cfg = cfg or load()
    path = f"/rest/connector-service/connectors/{source_id}/tools/{tool_name}/execute"
    return _request(cfg, "POST", path, {"parameters": arguments})
