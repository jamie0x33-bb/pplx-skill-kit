from __future__ import annotations

import pytest

from pplx_skill_kit import triage
from pplx_skill_kit.triage import Step

PROXY_VARS = (
    "PPLX_AGENT_PROXY_TOKEN",
    "PPLX_AGENT_PROXY_URL",
    "PPLX_CONNECTOR_TOOL_TARGET_BASE_URL",
    "SKILL_KIT_COLLECTOR",
)


@pytest.fixture
def bare(monkeypatch):
    """An environment with no proxy wiring, as on a developer machine."""
    for name in PROXY_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_steps_skip_cleanly_outside_a_sandbox(bare):
    assert triage.check_proxy().status == "skip"
    assert triage.check_allow_list().status == "skip"
    assert triage.check_listing().status == "skip"


def test_submit_is_skipped_without_a_bearer(bare):
    step = triage.submit([], "connector-403")
    assert step.status == "skip"
    assert "bearer" in step.detail


def test_run_stops_early_when_the_proxy_is_unreachable(bare, monkeypatch):
    monkeypatch.setattr(triage, "check_proxy", lambda: Step("proxy reachable", "fail", "timeout"))
    assert [s.name for s in triage.run()] == ["proxy reachable"]


def test_run_submits_only_when_asked(bare, monkeypatch):
    monkeypatch.setattr(triage, "check_proxy", lambda: Step("proxy reachable", "ok", "HTTP 200"))
    assert "submit bundle" not in [s.name for s in triage.run()]
    monkeypatch.setattr(triage, "submit", lambda *a, **k: Step("submit bundle", "ok", "filed x"))
    assert "submit bundle" in [s.name for s in triage.run(do_submit=True)]


def test_bundle_carries_counts_and_statuses():
    steps = [
        Step("allow list", "ok", "target accepted", {"status": 200}),
        Step("listing digest", "ok", "391 connectors, 17 connected",
             {"connectors": 391, "connected": 17}),
    ]
    payload = triage.bundle(steps, "connector-403")
    assert payload["symptom"] == "connector-403"
    assert payload["pairs"]["listing digest"]["connected"] == 17
    assert [s["status"] for s in payload["steps"]] == ["ok", "ok"]


def test_bundle_never_contains_a_credential(bare, monkeypatch):
    """The bearer authenticates the POST; it must not travel in the body."""
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_should-not-appear")
    steps = [Step("allow list", "ok", "target accepted", {"status": 200})]
    assert "agp_should-not-appear" not in repr(triage.bundle(steps, "connector-403"))


def test_summarize_names_the_stale_target_verdict():
    steps = [Step("allow list", "fail", "target is NOT on the allow list", {"status": 403})]
    assert "stale" in triage.summarize(steps, "connector-403")[-1]


def test_summarize_is_inconclusive_when_steps_were_skipped():
    steps = [Step("allow list", "skip", "no workspace bearer in this environment")]
    assert "inconclusive" in triage.summarize(steps, "connector-403")[-1]
