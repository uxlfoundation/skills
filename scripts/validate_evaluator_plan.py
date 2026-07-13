#!/usr/bin/env python3
"""Validate the machine-readable UXL skill evaluator plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "evaluation" / "uxl-skill-evaluator.v0.json"
SCHEMA = ROOT / "schemas" / "evaluator-plan.schema.json"
REQUIRED_ARMS = {"baseline", "skill_explicit"}
REQUIRED_TRACKS = {"static_skill_quality", "answer_quality_delta", "trace_quality", "executable_tasks", "hardware_backend"}
REQUIRED_DIMENSIONS = {
    "api_workflow_correctness",
    "build_and_runtime_correctness",
    "source_grounding",
    "correctness_validation",
    "unsupported_claim_avoidance",
}
REQUIRED_HARDWARE_TIERS = {"hosted_ci", "cpu_runner", "sycl_gpu_runner"}


def load_json(path: Path) -> tuple[dict, list[str]]:
    if not path.exists():
        return {}, [f"{path}: missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"{path}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"{path}: expected JSON object"]
    return data, []


def require_keys(name: str, item: dict, keys: set[str], errors: list[str]) -> None:
    missing = sorted(keys.difference(item))
    if missing:
        errors.append(f"{name}: missing keys: {', '.join(missing)}")


def unique_ids(section: str, items: object, errors: list[str]) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{section}: expected list")
        return set()
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{section}[{index}]: expected object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{section}[{index}]: missing string id")
            continue
        if item_id in seen:
            errors.append(f"{section}: duplicate id {item_id}")
        seen.add(item_id)
    return seen


def validate_plan(plan: dict) -> list[str]:
    errors: list[str] = []
    require_keys(
        str(PLAN),
        plan,
        {"schema_version", "name", "arms", "tracks", "dimensions", "hardware_tiers", "promotion_thresholds"},
        errors,
    )
    if plan.get("schema_version") != "0":
        errors.append(f"{PLAN}: schema_version must be '0'")
    if plan.get("name") != "uxl-skill-evaluator":
        errors.append(f"{PLAN}: name must be 'uxl-skill-evaluator'")

    arm_ids = unique_ids("arms", plan.get("arms"), errors)
    missing_arms = sorted(REQUIRED_ARMS.difference(arm_ids))
    if missing_arms:
        errors.append(f"{PLAN}: missing required arms: {', '.join(missing_arms)}")

    track_ids = unique_ids("tracks", plan.get("tracks"), errors)
    missing_tracks = sorted(REQUIRED_TRACKS.difference(track_ids))
    if missing_tracks:
        errors.append(f"{PLAN}: missing required tracks: {', '.join(missing_tracks)}")

    dimensions = plan.get("dimensions")
    dimension_ids = unique_ids("dimensions", dimensions, errors)
    missing_dimensions = sorted(REQUIRED_DIMENSIONS.difference(dimension_ids))
    if missing_dimensions:
        errors.append(f"{PLAN}: missing required dimensions: {', '.join(missing_dimensions)}")
    if isinstance(dimensions, list):
        total_weight = 0.0
        for item in dimensions:
            if not isinstance(item, dict):
                continue
            weight = item.get("weight")
            if not isinstance(weight, (int, float)) or weight <= 0:
                errors.append(f"{PLAN}: dimension {item.get('id', '<missing>')} has invalid weight")
            else:
                total_weight += float(weight)
        if abs(total_weight - 1.0) > 0.0001:
            errors.append(f"{PLAN}: dimension weights must sum to 1.0, got {total_weight:.4f}")

    hardware_ids = unique_ids("hardware_tiers", plan.get("hardware_tiers"), errors)
    missing_hardware = sorted(REQUIRED_HARDWARE_TIERS.difference(hardware_ids))
    if missing_hardware:
        errors.append(f"{PLAN}: missing required hardware tiers: {', '.join(missing_hardware)}")

    thresholds = plan.get("promotion_thresholds")
    if not isinstance(thresholds, dict):
        errors.append(f"{PLAN}: promotion_thresholds must be an object")
    else:
        if thresholds.get("minimum_answer_quality_tasks", 0) < 3:
            errors.append(f"{PLAN}: minimum_answer_quality_tasks should be at least 3")
        if thresholds.get("minimum_trials_per_arm", 0) < 2:
            errors.append(f"{PLAN}: minimum_trials_per_arm should be at least 2")
        if thresholds.get("maximum_critical_unsupported_claims") != 0:
            errors.append(f"{PLAN}: maximum_critical_unsupported_claims must be 0")
        if thresholds.get("requires_maintainer_review") is not True:
            errors.append(f"{PLAN}: requires_maintainer_review must be true")

    return errors


def main() -> int:
    schema, schema_errors = load_json(SCHEMA)
    plan, plan_errors = load_json(PLAN)
    errors = schema_errors + plan_errors
    if schema and schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{SCHEMA}: expected draft 2020-12 $schema")
    if plan:
        errors.extend(validate_plan(plan))

    if errors:
        print("Evaluator plan validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Evaluator plan validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
