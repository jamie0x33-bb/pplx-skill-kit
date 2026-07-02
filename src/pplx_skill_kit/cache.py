"""On-disk cache for connector tool schemas.

The connector listing is over a megabyte and rarely changes within a session, so
`describe` results are cached under ``~/.cache/pplx-skill-kit`` keyed by source id.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "pplx-skill-kit"
TTL_SECONDS = 3600


def _path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def get(key: str):
    p = _path(key)
    if not p.exists():
        return None
    if time.time() - p.stat().st_mtime > TTL_SECONDS:
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        p.unlink(missing_ok=True)
        return None


def put(key: str, value) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _path(key).with_suffix(".tmp")
    tmp.write_text(json.dumps(value))
    tmp.replace(_path(key))


def clear() -> int:
    if not CACHE_DIR.exists():
        return 0
    n = 0
    for p in CACHE_DIR.glob("*.json"):
        p.unlink()
        n += 1
    return n
