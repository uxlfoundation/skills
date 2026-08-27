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
ALLOWED_CALIBRATIONS = {"uncalibrated", "headroom", "ceiling", "no-lift", "manual"}
ALLOWED_TRACKS = {"executable", "answer-quality", "hardware"}
ALLOWED_REPRODUCTIONS = {"live", "fixture", "review"}
ALLOWED_ORIGINS = {
    "constructed",
    "maintainer-incident",
    "upstream-regression",
    "unassigned",
    "not-applicable",
}
ALLOWED_WORKFLOW_STAGES = {"reproduce", "investigate", "repair", "verify"}
ALLOWED_HARDWARE = {
    "none",
    "generic-cpu",
    "target-cpu",
    "target-gpu",
    "target-device",
    "target-distributed",
}
ALLOWED_ENVIRONMENTS = {
    "hosted-cpu",
    "hosted-container",
    "hosted-distributed",
    "hosted-toolchain",
    "manual-gpu",
    "target-cpu",
    "target-gpu",
    "target-device",
    "target-distributed",
}
ENVIRONMENT_HARDWARE = {
    "hosted-cpu": "generic-cpu",
    "hosted-container": "none",
    "hosted-distributed": "generic-cpu",
    "hosted-toolchain": "generic-cpu",
    "manual-gpu": "target-gpu",
    "target-cpu": "target-cpu",
    "target-gpu": "target-gpu",
    "target-device": "target-device",
    "target-distributed": "target-distributed",
}
TARGET_ENVIRONMENTS = {
    "manual-gpu",
    "target-cpu",
    "target-gpu",
    "target-device",
    "target-distributed",
}
REQUIRED_COMPARISON_ARMS = {"no-skill", "previous-skill", "candidate-skill"}
REQUIRED_EFFICIENCY_METRICS = {
    "uncached-input-tokens",
    "cached-input-tokens",
    "output-tokens",
    "cost-usd",
    "runtime-seconds",
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

    if data.get("schema_version") != "2.0":
        errors.append("schema_version must be '2.0'")

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

    comparison_arms = policy.get("comparison_arms")
    if (
        not isinstance(comparison_arms, list)
        or len(comparison_arms) != len(set(comparison_arms))
        or set(comparison_arms) != REQUIRED_COMPARISON_ARMS
    ):
        errors.append(
            "policy.comparison_arms must contain exactly "
            f"{sorted(REQUIRED_COMPARISON_ARMS)}"
        )

    triage = policy.get("triage")
    required_workflow: set[str] = set(ALLOWED_WORKFLOW_STAGES)
    accepted_origins = {"maintainer-incident", "upstream-regression"}
    if not isinstance(triage, dict):
        errors.append("policy.triage must be an object")
    else:
        configured_workflow = triage.get("required_workflow")
        if (
            not isinstance(configured_workflow, list)
            or len(configured_workflow) != len(set(configured_workflow))
            or set(configured_workflow) != ALLOWED_WORKFLOW_STAGES
        ):
            errors.append(
                "policy.triage.required_workflow must contain exactly "
                f"{sorted(ALLOWED_WORKFLOW_STAGES)}"
            )
        else:
            required_workflow = set(configured_workflow)
        if triage.get("requires_live_reproduction") is not True:
            errors.append("policy.triage.requires_live_reproduction must be true")
        configured_origins = triage.get("accepted_origins")
        if (
            not isinstance(configured_origins, list)
            or not configured_origins
            or len(configured_origins) != len(set(configured_origins))
            or not set(configured_origins).issubset(ALLOWED_ORIGINS)
            or "unassigned" in configured_origins
            or "constructed" in configured_origins
            or "not-applicable" in configured_origins
        ):
            errors.append(
                "policy.triage.accepted_origins must contain reviewed real-world origins"
            )
        else:
            accepted_origins = set(configured_origins)

    efficiency = policy.get("efficiency")
    if not isinstance(efficiency, dict):
        errors.append("policy.efficiency must be an object")
    else:
        if efficiency.get("quality_gate") != "verified-success":
            errors.append("policy.efficiency.quality_gate must be 'verified-success'")
        reward_floor = efficiency.get("verified_reward_floor")
        if not isinstance(reward_floor, (int, float)) or not 0 <= reward_floor <= 1:
            errors.append(
                "policy.efficiency.verified_reward_floor must be between 0 and 1"
            )
        if efficiency.get("primary_metric") != "total-tokens-per-verified-success":
            errors.append(
                "policy.efficiency.primary_metric must be "
                "'total-tokens-per-verified-success'"
            )
        required_metrics = efficiency.get("required_metrics")
        if not isinstance(required_metrics, list) or not REQUIRED_EFFICIENCY_METRICS.issubset(
            set(required_metrics)
        ):
            errors.append(
                "policy.efficiency.required_metrics is missing required telemetry"
            )
        desired_metrics = efficiency.get("desired_metrics")
        if not isinstance(desired_metrics, list):
            errors.append("policy.efficiency.desired_metrics must be an array")

    if policy.get("infrastructure_failure_policy") != "exclude-and-rerun":
        errors.append(
            "policy.infrastructure_failure_policy must be 'exclude-and-rerun'"
        )

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
        debugging_capability_ids: set[str] = set()
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
                if capability_class == "debugging" and isinstance(capability_id, str):
                    debugging_capability_ids.add(capability_id)
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
        live_workflow_debugging_ids: set[str] = set()
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
            environment = task.get("environment")
            reproduction = task.get("reproduction")
            origin = task.get("origin")
            hardware = task.get("hardware")
            _check_enum(errors, f"{name}.environment", environment, ALLOWED_ENVIRONMENTS)
            _check_enum(errors, f"{name}.reproduction", reproduction, ALLOWED_REPRODUCTIONS)
            _check_enum(errors, f"{name}.origin", origin, ALLOWED_ORIGINS)
            _check_enum(errors, f"{name}.hardware", hardware, ALLOWED_HARDWARE)
            workflow = task.get("workflow")
            workflow_stages: set[str] = set()
            if (
                not isinstance(workflow, list)
                or not workflow
                or len(workflow) != len(set(workflow))
                or not set(workflow).issubset(ALLOWED_WORKFLOW_STAGES)
            ):
                errors.append(
                    f"{name}.workflow must be a non-empty array of unique workflow stages"
                )
            else:
                workflow_stages = set(workflow)

            expected_hardware = ENVIRONMENT_HARDWARE.get(environment)
            if expected_hardware is not None and hardware != expected_hardware:
                errors.append(
                    f"{name}: environment {environment!r} requires hardware {expected_hardware!r}"
                )
            if reproduction == "live":
                if not {"reproduce", "verify"}.issubset(workflow_stages):
                    errors.append(
                        f"{name}: live reproduction must include reproduce and verify stages"
                    )
                if task.get("track") == "answer-quality":
                    errors.append(f"{name}: live reproduction cannot use answer-quality track")
                if environment == "hosted-container" or hardware == "none":
                    errors.append(f"{name}: live reproduction requires an executable environment")
            elif reproduction in {"fixture", "review"}:
                if {"reproduce", "verify"} & workflow_stages:
                    errors.append(
                        f"{name}: {reproduction} evaluation cannot claim reproduce or verify stages"
                    )
                if reproduction == "review" or task.get("track") == "answer-quality":
                    expected_fixture_environment = "hosted-container"
                    expected_fixture_hardware = "none"
                else:
                    expected_fixture_environment = "hosted-cpu"
                    expected_fixture_hardware = "generic-cpu"
                if (
                    environment != expected_fixture_environment
                    or hardware != expected_fixture_hardware
                ):
                    errors.append(
                        f"{name}: {reproduction} evaluation on track {task.get('track')!r} "
                        f"must use {expected_fixture_environment} with "
                        f"{expected_fixture_hardware} hardware"
                    )
                if reproduction == "review" and task.get("track") != "answer-quality":
                    errors.append(
                        f"{name}: review evaluation must use answer-quality track"
                    )
            if environment in TARGET_ENVIRONMENTS and reproduction != "live":
                errors.append(f"{name}: target environment requires live reproduction")
            if origin == "unassigned" and status == "implemented":
                errors.append(f"{name}: implemented task origin cannot be unassigned")
            if reproduction == "review" and origin != "not-applicable":
                errors.append(f"{name}: review task origin must be not-applicable")
            covers = task.get("covers")
            if not isinstance(covers, list) or not covers:
                errors.append(f"{name}.covers must be a non-empty array")
            else:
                invalid = set(covers) - capability_ids
                if invalid:
                    errors.append(f"{name}: covers unknown capabilities {sorted(invalid)}")
                covered_ids.update(item for item in covers if isinstance(item, str))
                if reproduction == "live" and required_workflow.issubset(workflow_stages):
                    live_workflow_debugging_ids.update(
                        item for item in covers if item in debugging_capability_ids
                    )

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
        missing_live_debugging = debugging_capability_ids - live_workflow_debugging_ids
        if missing_live_debugging:
            errors.append(
                f"{context}: debugging capabilities lack planned live end-to-end coverage "
                f"{sorted(missing_live_debugging)}"
            )

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
