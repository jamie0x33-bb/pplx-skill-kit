from pplx_skill_kit import cache


def test_put_and_get_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cache.put("gcal", {"tools": [1, 2]})
    assert cache.get("gcal") == {"tools": [1, 2]}


def test_get_missing_key_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    assert cache.get("nope") is None
