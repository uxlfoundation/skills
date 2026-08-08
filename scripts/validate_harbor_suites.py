#!/usr/bin/env python3
"""Validate the Harbor skill-suite and capability manifest."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evaluation" / "harbor" / "suites.json"
TASKS_ROOT = ROOT / "evaluation" / "harbor" / "tasks"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_CLASSES = {"correctness", "selection", "integration", "debugging", "performance"}
ALLOWED_STATUSES = {"implemented", "planned"}
ALLOWED_ROLES = {"smoke", "discriminating", "hardware"}
ALLOWED_CALIBRATIONS = {"uncalibrated", "headroom", "ceiling", "manual"}
ALLOWED_TRACKS = {"executable", "answer-quality", "hardware"}
ALLOWED_ENVIRONMENTS = {
    "hosted-cpu",
    "hosted-container",
    "hosted-distributed",
    "manual-gpu",
}


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def _check_enum(errors: list[str], context: str, value: Any, allowed: set[str]) -> None:
    if value not in allowed:
        errors.append(f"{context} has invalid value {value!r}; expected one of {sorted(allowed)}")


def _implemented_task_skill(task_name: str, tasks_root: Path) -> str | None:
    task_file = tasks_root / task_name / "task.toml"
    if not task_file.exists():
        return None
    try:
        data = tomllib.loads(task_file.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return "<invalid-task-toml>"
    metadata = data.get("metadata")
    return metadata.get("skill") if isinstance(metadata, dict) else None


def validate_manifest(
    data: dict[str, Any],
    *,
    skills_root: Path | None = None,
    tasks_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    skills_root = skills_root or ROOT / "skills"
    tasks_root = tasks_root or TASKS_ROOT

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    policy = data.get("policy")
    if not isinstance(policy, dict):
        return errors + ["policy must be an object"]
    minimum_tasks = policy.get("minimum_tasks_per_skill")
    minimum_discriminating = policy.get("minimum_discriminating_tasks_per_skill")
    if not isinstance(minimum_tasks, int) or minimum_tasks < 1:
        errors.append("policy.minimum_tasks_per_skill must be a positive integer")
        minimum_tasks = 1
    if not isinstance(minimum_discriminating, int) or minimum_discriminating < 1:
        errors.append("policy.minimum_discriminating_tasks_per_skill must be a positive integer")
        minimum_discriminating = 1

    required_classes = policy.get("required_capability_classes")
    if not isinstance(required_classes, list) or set(required_classes) != ALLOWED_CLASSES:
        errors.append(
            "policy.required_capability_classes must contain exactly "
            f"{sorted(ALLOWED_CLASSES)}"
        )

    attempts = policy.get("attempts")
    if not isinstance(attempts, dict):
        errors.append("policy.attempts must be an object")
    else:
        values = [attempts.get(name) for name in ("development_probe", "calibration", "promotion")]
        if not all(isinstance(value, int) and value > 0 for value in values):
            errors.append("all policy.attempts values must be positive integers")
        elif values != sorted(values):
            errors.append("policy.attempts must not decrease from development to promotion")

    thresholds = policy.get("promotion_thresholds")
    if not isinstance(thresholds, dict):
        errors.append("policy.promotion_thresholds must be an object")
    else:
        for name in ("maximum_task_mean_regression", "maximum_suite_mean_regression"):
            value = thresholds.get(name)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"policy.promotion_thresholds.{name} must be between 0 and 1")

    suites = data.get("suites")
    if not isinstance(suites, list):
        return errors + ["suites must be an array"]

    catalog_skills = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
    manifest_skills: list[str] = []
    task_names: set[str] = set()
    implemented_names: set[str] = set()

    for suite_index, suite in enumerate(suites):
        context = f"suites[{suite_index}]"
        if not isinstance(suite, dict):
            errors.append(f"{context} must be an object")
            continue
        skill = suite.get("skill")
        if not isinstance(skill, str):
            errors.append(f"{context}.skill must be a string")
            continue
        context = skill
        manifest_skills.append(skill)

        target = suite.get("target_task_count")
        if not isinstance(target, int) or target < minimum_tasks:
            errors.append(f"{context}: target_task_count must be at least {minimum_tasks}")

        capabilities = suite.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(f"{context}: capabilities must be a non-empty array")
            capabilities = []
        capability_ids: set[str] = set()
        capability_classes: set[str] = set()
        for capability in capabilities:
            if not isinstance(capability, dict):
                errors.append(f"{context}: capability must be an object")
                continue
            capability_id = capability.get("id")
            capability_class = capability.get("class")
            description = capability.get("description")
            if not isinstance(capability_id, str) or not NAME_RE.fullmatch(capability_id):
                errors.append(f"{context}: invalid capability id {capability_id!r}")
            elif capability_id in capability_ids:
                errors.append(f"{context}: duplicate capability id {capability_id}")
            else:
                capability_ids.add(capability_id)
            _check_enum(errors, f"{context}.{capability_id}.class", capability_class, ALLOWED_CLASSES)
            if isinstance(capability_class, str):
                capability_classes.add(capability_class)
            if not isinstance(description, str) or not description.strip():
                errors.append(f"{context}.{capability_id}: description must be non-empty")
        missing_classes = ALLOWED_CLASSES - capability_classes
        if missing_classes:
            errors.append(f"{context}: missing capability classes {sorted(missing_classes)}")

        tasks = suite.get("tasks")
        if not isinstance(tasks, list):
            errors.append(f"{context}: tasks must be an array")
            continue
        if isinstance(target, int) and len(tasks) < target:
            errors.append(f"{context}: has {len(tasks)} tasks but target_task_count is {target}")
        discriminating_count = sum(
            isinstance(task, dict) and task.get("role") == "discriminating" for task in tasks
        )
        if discriminating_count < minimum_discriminating:
            errors.append(
                f"{context}: requires at least {minimum_discriminating} discriminating tasks"
            )

        covered_ids: set[str] = set()
        for task_index, task in enumerate(tasks):
            task_context = f"{context}.tasks[{task_index}]"
            if not isinstance(task, dict):
                errors.append(f"{task_context} must be an object")
                continue
            name = task.get("name")
            if not isinstance(name, str) or not NAME_RE.fullmatch(name):
                errors.append(f"{task_context}: invalid task name {name!r}")
                continue
            if name in task_names:
                errors.append(f"duplicate task name {name}")
            task_names.add(name)
            status = task.get("status")
            calibration = task.get("calibration")
            _check_enum(errors, f"{name}.status", status, ALLOWED_STATUSES)
            _check_enum(errors, f"{name}.role", task.get("role"), ALLOWED_ROLES)
            _check_enum(errors, f"{name}.calibration", calibration, ALLOWED_CALIBRATIONS)
            _check_enum(errors, f"{name}.track", task.get("track"), ALLOWED_TRACKS)
            _check_enum(errors, f"{name}.environment", task.get("environment"), ALLOWED_ENVIRONMENTS)
            covers = task.get("covers")
            if not isinstance(covers, list) or not covers:
                errors.append(f"{name}.covers must be a non-empty array")
            else:
                invalid = set(covers) - capability_ids
                if invalid:
                    errors.append(f"{name}: covers unknown capabilities {sorted(invalid)}")
                covered_ids.update(item for item in covers if isinstance(item, str))

            task_path_exists = (tasks_root / name / "task.toml").exists()
            if status == "implemented":
                implemented_names.add(name)
                if not task_path_exists:
                    errors.append(f"{name}: implemented task directory is missing")
                else:
                    actual_skill = _implemented_task_skill(name, tasks_root)
                    if actual_skill != skill:
                        errors.append(
                            f"{name}: task metadata skill {actual_skill!r} does not match {skill!r}"
                        )
            elif status == "planned":
                if task_path_exists:
                    errors.append(f"{name}: task directory exists but manifest status is planned")
                if calibration != "uncalibrated":
                    errors.append(f"{name}: planned task calibration must be uncalibrated")

        uncovered = capability_ids - covered_ids
        if uncovered:
            errors.append(f"{context}: capabilities have no planned task coverage {sorted(uncovered)}")

    if sorted(manifest_skills) != catalog_skills:
        errors.append("manifest skill list does not match the skills directory")
    if len(manifest_skills) != len(set(manifest_skills)):
        errors.append("manifest contains duplicate skill suites")

    actual_task_names = {
        path.name for path in tasks_root.iterdir() if path.is_dir() and (path / "task.toml").exists()
    }
    missing_from_manifest = actual_task_names - implemented_names
    missing_on_disk = implemented_names - actual_task_names
    if missing_from_manifest:
        errors.append(f"implemented Harbor tasks missing from manifest: {sorted(missing_from_manifest)}")
    if missing_on_disk:
        errors.append(f"manifest implemented tasks missing on disk: {sorted(missing_on_disk)}")
    return errors


def main() -> int:
    try:
        data = load_manifest()
    except ValueError as exc:
        print(f"Harbor suite validation failed: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(data)
    if errors:
        print("Harbor suite validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    suites = data["suites"]
    task_count = sum(len(suite["tasks"]) for suite in suites)
    implemented = sum(
        task["status"] == "implemented" for suite in suites for task in suite["tasks"]
    )
    print(
        f"Harbor suite validation passed: {len(suites)} skills, "
        f"{task_count} total tasks, {implemented} implemented."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
