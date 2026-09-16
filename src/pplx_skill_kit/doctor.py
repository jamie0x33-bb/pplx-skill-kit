"""Environment diagnostics.

`doctor` answers one question: is this environment wired up well enough for a skill
to reach its connectors? It reports what it resolved, never credential values --
secrets are reduced to a short SHA-256 prefix so two environments can be compared
without either one being disclosed.
"""

from __future__ import annotations

import hashlib
import os
import platform
import sys

from . import __version__
from .config import in_sandbox, load

SECRET_ENV = (
    "PPLX_AGENT_PROXY_TOKEN",
    "PPLX_CONNECTOR_API_KEY",
    "PPLX_SDK_API_KEY",
    "PPLX_LLM_API_KEY",
    "PPLX_CLI_TELEMETRY_API_KEY",
)

PAIRS = (
    ("PPLX_CONNECTOR_BASE_URL", "PPLX_CONNECTOR_TOOL_TARGET_BASE_URL"),
    ("PPLX_CONNECTOR_CONTROL_PLANE_BASE_URL", "PPLX_CONNECTOR_CONTROL_PLANE_TARGET_BASE_URL"),
    ("PPLX_CLI_TELEMETRY_BASE_URL", "PPLX_CLI_TELEMETRY_TARGET_BASE_URL"),
    ("PPLX_SDK_BASE_URL", "PPLX_SDK_TARGET_BASE_URL"),
)


def fingerprint(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def report() -> dict:
    cfg = load()
    return {
        "skill_kit_version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "sandbox": in_sandbox(),
        "agent_id": cfg.agent_id,
        "connector": {
            "base_url": cfg.base_url,
            "target_base_url": cfg.target_base_url,
            "usable": cfg.usable,
        },
        "pairs": {
            public: {
                "public": os.environ.get(public),
                "target": os.environ.get(target),
                "complete": bool(os.environ.get(public) and os.environ.get(target)),
            }
            for public, target in PAIRS
        },
        "secret_fingerprints": {name: fingerprint(os.environ.get(name)) for name in SECRET_ENV},
    }


def summarize(rep: dict) -> list[str]:
    lines = [f"skill-kit {rep['skill_kit_version']} on python {rep['python']}"]
    lines.append("sandbox: yes" if rep["sandbox"] else "sandbox: no")
    c = rep["connector"]
    lines.append(f"connector base:   {c['base_url'] or '(unset)'}")
    lines.append(f"connector target: {c['target_base_url'] or '(unset)'}")
    for public, info in rep["pairs"].items():
        state = "ok" if info["complete"] else "INCOMPLETE"
        lines.append(f"  {state:<10} {public}")
    missing = [k for k, v in rep["secret_fingerprints"].items() if v is None]
    if missing:
        lines.append("unset credentials: " + ", ".join(missing))
    if not c["usable"]:
        lines.append("connector calls will fail; see https://pplx-skill-kit.vercel.app/docs/preflight")
    else:
        lines.append("connector calls should work")
    return lines
