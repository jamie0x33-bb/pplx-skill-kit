"""Scaffold and validate skill directories against the Agent Skills layout."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
REQUIRED_KEYS = ("name", "description")

TEMPLATE = """---
name: {name}
description: {description}
---

# {title}

## When to use this

Describe the situations this skill applies to.

## Steps

1. ...
"""


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def scaffold(root: Path, name: str, description: str) -> Path:
    d = root / name
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    (d / "references").mkdir(exist_ok=True)
    title = name.replace("-", " ").title()
    (d / "SKILL.md").write_text(TEMPLATE.format(name=name, description=description, title=title))
    return d


def validate(directory: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    skill_md = directory / "SKILL.md"
    if not skill_md.exists():
        return ValidationResult(False, ["SKILL.md is missing"])

    text = skill_md.read_text()
    m = FRONTMATTER.match(text)
    if not m:
        errors.append("SKILL.md has no YAML frontmatter block")
    else:
        keys = {line.split(":", 1)[0].strip() for line in m.group(1).splitlines() if ":" in line}
        for required in REQUIRED_KEYS:
            if required not in keys:
                errors.append(f"frontmatter is missing '{required}'")

    body = text[m.end():] if m else text
    if not body.strip():
        errors.append("SKILL.md has no body after the frontmatter")
    if len(body) > 40_000:
        warnings.append("SKILL.md body is very long; consider moving detail into references/")
    if not (directory / "scripts").exists():
        warnings.append("no scripts/ directory")

    return ValidationResult(not errors, errors, warnings)
