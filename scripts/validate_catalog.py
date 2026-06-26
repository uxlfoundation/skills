#!/usr/bin/env python3
"""Validate the local UXL skill catalog without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SKILL_CARDS = ROOT / "skill-cards"
MANIFEST = ROOT / "skills.yaml"
SCHEMAS = ROOT / "schemas"
RELEASES = ROOT / "docs" / "releases"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\((references/[^)]+|scripts/[^)]+|evals/[^)]+)\)")
ALLOWED_CATALOG_STATUSES = {"incubating", "pilot", "released"}
ALLOWED_STATUSES = {"incubating", "pilot", "reviewed", "project-owned"}
REQUIRED_MANIFEST_KEYS = {
    "name",
    "status",
    "owner_project",
    "owner_repo",
    "catalog_path",
    "skill_card",
    "source_of_truth_target",
    "maintainer_review",
}
REQUIRED_SCHEMA_FILES = [
    "skills.schema.json",
    "evals.schema.json",
]
REQUIRED_AGENT_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "CONVENTIONS.md",
    ".aider.conf.yml",
    ".windsurfrules",
    ".github/copilot-instructions.md",
    ".github/instructions/uxl-skills.instructions.md",
    ".cursor/rules/uxl-skills.mdc",
    ".continue/rules/uxl-skills.md",
    ".clinerules/uxl-skills.md",
    ".agents/skills/uxl-skills-catalog.md",
]


def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter marker")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter marker")
    block = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"{skill_dir}: missing SKILL.md"]

    try:
        frontmatter, body = read_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{skill_file}: {exc}"]

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if name != skill_dir.name:
        errors.append(f"{skill_file}: name {name!r} does not match directory {skill_dir.name!r}")
    if not NAME_RE.match(name):
        errors.append(f"{skill_file}: invalid skill name {name!r}")
    if not description or "TODO" in description:
        errors.append(f"{skill_file}: missing real description")
    if len(description) > 1024:
        errors.append(f"{skill_file}: description exceeds 1024 characters")
    if "TODO" in body or "[TODO" in body:
        errors.append(f"{skill_file}: body still contains TODO placeholder text")
    if len(body.splitlines()) > 500:
        errors.append(f"{skill_file}: body exceeds 500-line guideline")

    text = skill_file.read_text(encoding="utf-8")
    for rel in LINK_RE.findall(text):
        target = skill_dir / rel
        if not target.exists():
            errors.append(f"{skill_file}: linked resource does not exist: {rel}")

    eval_file = skill_dir / "evals" / "evals.json"
    if eval_file.exists():
        try:
            data = json.loads(eval_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{eval_file}: invalid JSON: {exc}")
        else:
            if data.get("skill_name") != skill_dir.name:
                errors.append(f"{eval_file}: skill_name does not match directory")
            evals = data.get("evals")
            if not isinstance(evals, list) or not evals:
                errors.append(f"{eval_file}: evals must be a non-empty list")
            else:
                ids: set[str] = set()
                for item in evals:
                    for key in ("id", "prompt", "expected_output"):
                        if key not in item:
                            errors.append(f"{eval_file}: eval item missing {key}")
                    eval_id = item.get("id")
                    if eval_id in ids:
                        errors.append(f"{eval_file}: duplicate eval id {eval_id}")
                    ids.add(eval_id)
                    checks = item.get("checks")
                    if not isinstance(checks, dict):
                        errors.append(f"{eval_file}: eval {eval_id} missing checks object")
                    else:
                        must_include = checks.get("must_include")
                        must_not_include = checks.get("must_not_include", [])
                        if not isinstance(must_include, list) or not must_include:
                            errors.append(f"{eval_file}: eval {eval_id} checks.must_include must be non-empty")
                        if not isinstance(must_not_include, list):
                            errors.append(f"{eval_file}: eval {eval_id} checks.must_not_include must be a list")
    else:
        errors.append(f"{skill_dir}: missing evals/evals.json")

    return errors


def validate_manifest(skill_names: list[str]) -> list[str]:
    errors: list[str] = []
    if not MANIFEST.exists():
        return [f"{MANIFEST}: missing catalog manifest"]

    text = MANIFEST.read_text(encoding="utf-8")
    entries = parse_manifest_entries(text)
    scalars = parse_top_level_scalars(text)
    manifest_names = [entry.get("name", "") for entry in entries]
    if sorted(manifest_names) != sorted(skill_names):
        errors.append(f"{MANIFEST}: manifest skill list does not match skills directory")
    if 'schema_version: "1"' not in text:
        errors.append(f"{MANIFEST}: missing schema_version 1")
    catalog_status = scalars.get("catalog_status")
    if catalog_status not in ALLOWED_CATALOG_STATUSES:
        errors.append(f"{MANIFEST}: invalid catalog_status {catalog_status!r}")
    if catalog_status == "released" and not any(RELEASES.glob("*.md")):
        errors.append(f"{MANIFEST}: released catalog requires at least one docs/releases/*.md ledger entry")
    if not entries:
        errors.append(f"{MANIFEST}: no skill entries parsed")
    for entry in entries:
        name = entry.get("name", "<missing>")
        missing = sorted(REQUIRED_MANIFEST_KEYS.difference(entry))
        if missing:
            errors.append(f"{MANIFEST}: {name} missing keys: {', '.join(missing)}")
        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{MANIFEST}: {name} has invalid status {status!r}")
        if status in {"pilot", "reviewed", "project-owned"} and "last_source_verification" not in entry:
            errors.append(f"{MANIFEST}: {name} status {status!r} requires last_source_verification")
        if status in {"reviewed", "project-owned"} and entry.get("maintainer_review") == "needed":
            errors.append(f"{MANIFEST}: {name} status {status!r} requires maintainer_review evidence")
        owner_repo = entry.get("owner_repo", "")
        if owner_repo and not owner_repo.startswith("https://github.com/uxlfoundation/"):
            errors.append(f"{MANIFEST}: {name} owner_repo should point at uxlfoundation GitHub")
    for name in skill_names:
        required = [
            f'catalog_path: "skills/{name}"',
            f'skill_card: "skill-cards/{name}.md"',
        ]
        for needle in required:
            if needle not in text:
                errors.append(f"{MANIFEST}: missing {needle}")
    return errors


def parse_manifest_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            remainder = stripped[2:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip().strip('"')
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip('"')
    if current is not None:
        entries.append(current)
    return entries


def parse_top_level_scalars(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        if raw_line.startswith(" ") or raw_line.startswith("-"):
            continue
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def validate_skill_cards(skill_names: list[str]) -> list[str]:
    errors: list[str] = []
    if not SKILL_CARDS.exists():
        return [f"{SKILL_CARDS}: missing skill-cards directory"]
    for name in skill_names:
        card = SKILL_CARDS / f"{name}.md"
        if not card.exists():
            errors.append(f"{card}: missing skill card")
            continue
        text = card.read_text(encoding="utf-8")
        for heading in ("## Status", "## Purpose", "## Supported Tasks", "## Limitations", "## Evidence"):
            if heading not in text:
                errors.append(f"{card}: missing {heading}")
        if name not in text:
            errors.append(f"{card}: card does not mention skill name")
    return errors


def validate_schemas() -> list[str]:
    errors: list[str] = []
    if not SCHEMAS.exists():
        return [f"{SCHEMAS}: missing schemas directory"]
    for rel in REQUIRED_SCHEMA_FILES:
        path = SCHEMAS / rel
        if not path.exists():
            errors.append(f"{path}: missing schema file")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON schema file: {exc}")
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path}: expected draft 2020-12 $schema")
    return errors


def validate_agent_files() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_AGENT_FILES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{path}: missing agent instruction file")
        elif path.stat().st_size == 0:
            errors.append(f"{path}: empty agent instruction file")
    return errors


def main() -> int:
    if not SKILLS.exists():
        print(f"Missing skills directory: {SKILLS}", file=sys.stderr)
        return 1

    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    skill_names = [p.name for p in skill_dirs]
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))
    errors.extend(validate_manifest(skill_names))
    errors.extend(validate_skill_cards(skill_names))
    errors.extend(validate_schemas())
    errors.extend(validate_agent_files())

    if errors:
        print("Catalog validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Catalog validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
