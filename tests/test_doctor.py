from pplx_skill_kit import doctor


def test_fingerprint_is_short_and_stable():
    a = doctor.fingerprint("secret-value")
    assert a == doctor.fingerprint("secret-value")
    assert len(a) == 12
    assert "secret-value" not in a


def test_fingerprint_of_unset_is_none():
    assert doctor.fingerprint(None) is None
    assert doctor.fingerprint("") is None


def test_report_never_contains_raw_secrets(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_supersecret")
    rep = doctor.report()
    assert "agp_supersecret" not in repr(rep)
    assert rep["secret_fingerprints"]["PPLX_AGENT_PROXY_TOKEN"] is not None
