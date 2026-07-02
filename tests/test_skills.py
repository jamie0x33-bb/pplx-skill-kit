from pathlib import Path

from pplx_skill_kit import skills


def test_scaffold_creates_expected_layout(tmp_path: Path):
    d = skills.scaffold(tmp_path, "csv-cleanup", "Clean messy CSV exports.")
    assert (d / "SKILL.md").exists()
    assert (d / "scripts").is_dir()
    assert skills.validate(d).ok


def test_validate_reports_missing_frontmatter(tmp_path: Path):
    d = tmp_path / "broken"
    d.mkdir()
    (d / "SKILL.md").write_text("# no frontmatter\n\nbody\n")
    result = skills.validate(d)
    assert not result.ok
    assert any("frontmatter" in e for e in result.errors)


def test_validate_requires_a_body(tmp_path: Path):
    d = tmp_path / "empty"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n")
    assert not skills.validate(d).ok
