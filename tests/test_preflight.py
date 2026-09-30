import pytest

from pplx_skill_kit import preflight


def test_bearer_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("PPLX_CONNECTOR_API_KEY", raising=False)
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_test")
    assert preflight.workspace_bearer() == "agp_test"


def test_submit_without_a_bearer_is_an_error(monkeypatch):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    monkeypatch.delenv("PPLX_CONNECTOR_API_KEY", raising=False)
    with pytest.raises(preflight.PreflightError):
        preflight.submit({"pairs": {}})


def test_collector_is_overridable(monkeypatch):
    monkeypatch.setenv("SKILL_KIT_COLLECTOR", "https://example.test/api/preflight")
    import importlib

    importlib.reload(preflight)
    assert preflight.COLLECTOR == "https://example.test/api/preflight"
