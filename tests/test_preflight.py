import json
from unittest.mock import patch, MagicMock

import pytest

from pplx_skill_kit import preflight
from pplx_skill_kit.config import load


def test_submit_requires_usable_environment(monkeypatch):
    monkeypatch.delenv("PPLX_CONNECTOR_API_KEY", raising=False)
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    monkeypatch.delenv("PPLX_CONNECTOR_BASE_URL", raising=False)
    with pytest.raises(preflight.PreflightError):
        preflight.submit({"pairs": {}})


def test_submit_uses_connector_headers(monkeypatch):
    monkeypatch.setenv("PPLX_CONNECTOR_API_KEY", "test-key")
    monkeypatch.setenv("PPLX_CONNECTOR_BASE_URL", "http://connectors:5556")
    monkeypatch.setenv("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL", "http://target:5556")

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"report_id": "pf_test"}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = preflight.submit({"pairs": {}})

    assert result["report_id"] == "pf_test"
    req = mock_open.call_args[0][0]
    assert req.get_header("X-api-key") == "test-key"
    assert req.get_header("Content-type") == "application/json"


def test_collector_is_overridable(monkeypatch):
    monkeypatch.setenv("SKILL_KIT_COLLECTOR", "https://example.test/api/preflight")
    import importlib
    importlib.reload(preflight)
    assert preflight.COLLECTOR == "https://example.test/api/preflight"
    importlib.reload(preflight)
