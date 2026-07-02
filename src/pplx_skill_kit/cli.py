from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, cache, connectors, doctor, skills


def _doctor(args) -> int:
    rep = doctor.report()
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print("\n".join(doctor.summarize(rep)))
    return 0 if rep["connector"]["usable"] else 1


def _list(args) -> int:
    items = connectors.connected() if args.connected else connectors.list_connectors()
    if args.json:
        print(json.dumps(items, indent=2))
        return 0
    for c in items:
        print(f"{c.get('status','?'):<13} {c.get('source_id',''):<26} {len(c.get('tools', []))} tools")
    return 0


def _describe(args) -> int:
    cached = cache.get(args.source_id)
    if cached is None:
        cached = connectors.describe(args.source_id)
        cache.put(args.source_id, cached)
    print(json.dumps(cached, indent=2))
    return 0


def _call(args) -> int:
    arguments = json.loads(args.arguments) if args.arguments else {}
    print(json.dumps(connectors.call_tool(args.source_id, args.tool, arguments), indent=2))
    return 0


def _new(args) -> int:
    path = skills.scaffold(Path(args.directory), args.name, args.description)
    print(f"created {path}")
    return 0


def _validate(args) -> int:
    result = skills.validate(Path(args.directory))
    for e in result.errors:
        print(f"error:   {e}")
    for w in result.warnings:
        print(f"warning: {w}")
    print("valid" if result.ok else "invalid")
    return 0 if result.ok else 1


def _clear_cache(args) -> int:
    print(f"removed {cache.clear()} cached schemas")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="skill-kit", description="Perplexity Computer skill toolkit")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("doctor", help="check the connector environment")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=_doctor)

    l = sub.add_parser("list", help="list connectors")
    l.add_argument("--connected", action="store_true")
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=_list)

    de = sub.add_parser("describe", help="describe one connector's tools")
    de.add_argument("source_id")
    de.set_defaults(func=_describe)

    ca = sub.add_parser("call", help="call a connector tool")
    ca.add_argument("source_id")
    ca.add_argument("tool")
    ca.add_argument("--arguments", help="JSON object")
    ca.set_defaults(func=_call)

    n = sub.add_parser("new", help="scaffold a skill directory")
    n.add_argument("name")
    n.add_argument("--description", default="Describe when this skill applies.")
    n.add_argument("--directory", default=".")
    n.set_defaults(func=_new)

    v = sub.add_parser("validate", help="validate a skill directory")
    v.add_argument("directory")
    v.set_defaults(func=_validate)

    cc = sub.add_parser("clear-cache", help="drop cached tool schemas")
    cc.set_defaults(func=_clear_cache)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except connectors.ConnectorError as exc:
        print(f"connector service error {exc.status}: {exc.body[:300]}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
