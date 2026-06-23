"""Resolve the connector runtime configuration from the sandbox environment.

Computer injects the connector wiring as environment variables at process start.
Each service is a pair: a public base URL that requests are sent to, and an
internal target base URL that the pass-through proxy forwards to. The proxy
rejects any request whose ``X-Base-Url`` is not in the session's allowed set, so
both halves of the pair have to be read together.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorConfig:
    base_url: str | None
    target_base_url: str | None
    api_key: str | None
    agent_id: str | None

    @property
    def usable(self) -> bool:
        return all((self.base_url, self.target_base_url, self.api_key))

    def headers(self) -> dict[str, str]:
        """Headers for a connector-service call through the pass-through proxy."""
        h = {
            "x-api-key": self.api_key or "",
            "x-app-apiclient": "asi-sandbox",
            "content-type": "application/json",
        }
        if self.target_base_url:
            h["X-Base-Url"] = self.target_base_url
        if self.agent_id:
            h["x-agent-id"] = self.agent_id
        return h


def load() -> ConnectorConfig:
    return ConnectorConfig(
        base_url=os.environ.get("PPLX_CONNECTOR_BASE_URL"),
        target_base_url=os.environ.get("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL"),
        api_key=os.environ.get("PPLX_CONNECTOR_API_KEY") or os.environ.get("PPLX_AGENT_PROXY_TOKEN"),
        agent_id=os.environ.get("ASI_EXTERNAL_TOOLS_AGENT_ID") or os.environ.get("PPLX_CLI_TELEMETRY_AGENT_ID"),
    )


def in_sandbox() -> bool:
    return os.environ.get("SANDBOX_TYPE") == "asi_session"
