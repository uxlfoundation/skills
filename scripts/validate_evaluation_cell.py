#!/usr/bin/env python3
"""Validate a matched UXL evaluation-cell record and report staleness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARMS = ("no-skill", "previous-skill", "candidate-skill")
STAGE_MINIMUM_ATTEMPTS = {"development": 1, "calibration": 3, "promotion": 5}
ENVIRONMENTS = {
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
HARDWARE_CLASSES = {
    "none",
    "generic-cpu",
    "target-cpu",
    "target-gpu",
    "target-device",
    "target-distributed",
}
MATERIAL_DIMENSIONS = {
    "scope.task_revision.content_sha256",
    "scope.task_dirty",
    "scope.verifier_sha256",
    "treatment.previous_skill.content_sha256",
    "treatment.candidate_skill.content_sha256",
    "agent.name",
    "agent.harness",
    "agent.harness_version",
    "agent.model",
    "agent.reasoning_effort",
    "execution.environment",
    "execution.os",
    "execution.architecture",
    "execution.container_image",
    "execution.container_digest",
    "execution.toolchain",
    "execution.hardware.class",
    "execution.hardware.probe_sha256",
    "execution.attempts_per_arm",
    "execution.timeout_seconds",
    "execution.concurrency",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
CONTAINER_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def _object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _required_keys(
    value: dict[str, Any], required: set[str], allowed: set[str], path: str, errors: list[str]
) -> None:
    for name in sorted(required - set(value)):
        errors.append(f"{path}.{name} is required")
    for name in sorted(set(value) - allowed):
        errors.append(f"{path}.{name} is not allowed")


def _nonempty_string(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def _integer(value: Any, path: str, errors: list[str], minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        errors.append(f"{path} must be an integer >= {minimum}")


def _revision(value: Any, path: str, errors: list[str]) -> None:
    revision = _object(value, path, errors)
    keys = {"repository", "commit", "content_sha256"}
    _required_keys(revision, keys, keys, path, errors)
    _nonempty_string(revision.get("repository"), f"{path}.repository", errors)
    commit = revision.get("commit")
    if not isinstance(commit, str) or not COMMIT_PATTERN.fullmatch(commit):
        errors.append(f"{path}.commit must be a lowercase 40-character Git SHA")
    digest = revision.get("content_sha256")
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        errors.append(f"{path}.content_sha256 must be a lowercase SHA-256 digest")


def _timestamp(value: Any, path: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{path} must be an ISO-8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{path} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def validate_record(record: Any) -> list[str]:
    errors: list[str] = []
    root = _object(record, "record", errors)
    root_keys = {
        "schema_version",
        "cell_id",
        "stage",
        "recorded_at",
        "scope",
        "treatment",
        "agent",
        "execution",
        "results",
        "freshness",
    }
    _required_keys(root, root_keys, root_keys, "record", errors)
    if root.get("schema_version") != "1.0":
        errors.append("record.schema_version must be '1.0'")
    cell_id = root.get("cell_id")
    if not isinstance(cell_id, str) or not NAME_PATTERN.fullmatch(cell_id):
        errors.append("record.cell_id must be a lowercase kebab-case name")
    stage = root.get("stage")
    if stage not in STAGE_MINIMUM_ATTEMPTS:
        errors.append("record.stage must be development, calibration, or promotion")
    _timestamp(root.get("recorded_at"), "record.recorded_at", errors)

    scope = _object(root.get("scope"), "record.scope", errors)
    scope_keys = {"skill", "task", "task_revision", "task_dirty", "verifier_sha256"}
    _required_keys(scope, scope_keys, scope_keys, "record.scope", errors)
    for name in ("skill", "task"):
        value = scope.get(name)
        if not isinstance(value, str) or not NAME_PATTERN.fullmatch(value):
            errors.append(f"record.scope.{name} must be a lowercase kebab-case name")
    _revision(scope.get("task_revision"), "record.scope.task_revision", errors)
    if not isinstance(scope.get("task_dirty"), bool):
        errors.append("record.scope.task_dirty must be boolean")
    verifier = scope.get("verifier_sha256")
    if not isinstance(verifier, str) or not SHA256_PATTERN.fullmatch(verifier):
        errors.append("record.scope.verifier_sha256 must be a lowercase SHA-256 digest")

    treatment = _object(root.get("treatment"), "record.treatment", errors)
    treatment_keys = {
        "comparison_arms",
        "previous_skill",
        "candidate_skill",
        "candidate_dirty",
    }
    _required_keys(treatment, treatment_keys, treatment_keys, "record.treatment", errors)
    if treatment.get("comparison_arms") != list(ARMS):
        errors.append(f"record.treatment.comparison_arms must equal {list(ARMS)}")
    _revision(treatment.get("previous_skill"), "record.treatment.previous_skill", errors)
    _revision(treatment.get("candidate_skill"), "record.treatment.candidate_skill", errors)
    if not isinstance(treatment.get("candidate_dirty"), bool):
        errors.append("record.treatment.candidate_dirty must be boolean")
    previous = treatment.get("previous_skill")
    candidate = treatment.get("candidate_skill")
    if isinstance(previous, dict) and isinstance(candidate, dict):
        if previous.get("content_sha256") == candidate.get("content_sha256"):
            errors.append("previous and candidate skill content digests must differ")
    if stage == "promotion" and treatment.get("candidate_dirty") is not False:
        errors.append("promotion evidence requires candidate_dirty=false")
    if stage == "promotion" and scope.get("task_dirty") is not False:
        errors.append("promotion evidence requires task_dirty=false")

    agent = _object(root.get("agent"), "record.agent", errors)
    agent_keys = {"name", "harness", "harness_version", "model", "reasoning_effort"}
    _required_keys(agent, agent_keys, agent_keys, "record.agent", errors)
    for name in sorted(agent_keys):
        _nonempty_string(agent.get(name), f"record.agent.{name}", errors)

    execution = _object(root.get("execution"), "record.execution", errors)
    execution_keys = {
        "environment",
        "os",
        "architecture",
        "container_image",
        "container_digest",
        "toolchain",
        "hardware",
        "attempts_per_arm",
        "timeout_seconds",
        "concurrency",
    }
    _required_keys(execution, execution_keys, execution_keys, "record.execution", errors)
    if execution.get("environment") not in ENVIRONMENTS:
        errors.append("record.execution.environment is not a supported environment")
    for name in ("os", "architecture"):
        _nonempty_string(execution.get(name), f"record.execution.{name}", errors)
    container_image = execution.get("container_image")
    if container_image is not None:
        _nonempty_string(container_image, "record.execution.container_image", errors)
    container_digest = execution.get("container_digest")
    if container_digest is not None and (
        not isinstance(container_digest, str)
        or not CONTAINER_DIGEST_PATTERN.fullmatch(container_digest)
    ):
        errors.append("record.execution.container_digest must be null or sha256:<64 hex>")
    if container_digest is not None and container_image is None:
        errors.append("record.execution.container_image is required when a digest is recorded")
    toolchain = _object(execution.get("toolchain"), "record.execution.toolchain", errors)
    if not toolchain:
        errors.append("record.execution.toolchain must contain at least one version")
    for name, value in toolchain.items():
        _nonempty_string(name, "record.execution.toolchain key", errors)
        _nonempty_string(value, f"record.execution.toolchain.{name}", errors)
    hardware = _object(execution.get("hardware"), "record.execution.hardware", errors)
    hardware_keys = {"class", "probe_sha256"}
    _required_keys(hardware, hardware_keys, hardware_keys, "record.execution.hardware", errors)
    hardware_class = hardware.get("class")
    if hardware_class not in HARDWARE_CLASSES:
        errors.append("record.execution.hardware.class is not supported")
    probe = hardware.get("probe_sha256")
    if probe is not None and (not isinstance(probe, str) or not SHA256_PATTERN.fullmatch(probe)):
        errors.append("record.execution.hardware.probe_sha256 must be null or a SHA-256 digest")
    if hardware_class not in {None, "none", "generic-cpu"} and probe is None:
        errors.append("specialized hardware evidence requires a probe_sha256")
    for name in ("attempts_per_arm", "timeout_seconds", "concurrency"):
        _integer(execution.get(name), f"record.execution.{name}", errors, 1)
    attempts = execution.get("attempts_per_arm")
    if stage in STAGE_MINIMUM_ATTEMPTS and isinstance(attempts, int):
        minimum = STAGE_MINIMUM_ATTEMPTS[stage]
        if attempts < minimum:
            errors.append(f"{stage} evidence requires at least {minimum} attempts per arm")

    results = _object(root.get("results"), "record.results", errors)
    results_keys = {"reward_floor", "arms"}
    _required_keys(results, results_keys, results_keys, "record.results", errors)
    reward_floor = results.get("reward_floor")
    if isinstance(reward_floor, bool) or not isinstance(reward_floor, (int, float)) or not 0 <= reward_floor <= 1:
        errors.append("record.results.reward_floor must be between 0 and 1")
    arms = _object(results.get("arms"), "record.results.arms", errors)
    _required_keys(arms, set(ARMS), set(ARMS), "record.results.arms", errors)
    arm_keys = {
        "result_path",
        "accepted_attempts",
        "completed_attempts",
        "errored_attempts",
        "excluded_infrastructure_failures",
        "mean_reward",
        "verified_successes",
    }
    for arm_name in ARMS:
        arm = _object(arms.get(arm_name), f"record.results.arms.{arm_name}", errors)
        _required_keys(arm, arm_keys, arm_keys, f"record.results.arms.{arm_name}", errors)
        _nonempty_string(arm.get("result_path"), f"record.results.arms.{arm_name}.result_path", errors)
        for name in (
            "accepted_attempts",
            "completed_attempts",
            "errored_attempts",
            "excluded_infrastructure_failures",
            "verified_successes",
        ):
            _integer(arm.get(name), f"record.results.arms.{arm_name}.{name}", errors, 0)
        mean_reward = arm.get("mean_reward")
        if isinstance(mean_reward, bool) or not isinstance(mean_reward, (int, float)) or not 0 <= mean_reward <= 1:
            errors.append(f"record.results.arms.{arm_name}.mean_reward must be between 0 and 1")
        accepted = arm.get("accepted_attempts")
        completed = arm.get("completed_attempts")
        errored = arm.get("errored_attempts")
        verified = arm.get("verified_successes")
        if isinstance(attempts, int) and accepted != attempts:
            errors.append(f"{arm_name} accepted_attempts must equal execution.attempts_per_arm")
        if isinstance(accepted, int) and completed != accepted:
            errors.append(f"{arm_name} completed_attempts must equal accepted_attempts")
        if errored != 0:
            errors.append(f"{arm_name} errored_attempts must be zero; exclude and rerun infrastructure failures")
        if isinstance(completed, int) and isinstance(verified, int) and verified > completed:
            errors.append(f"{arm_name} verified_successes cannot exceed completed_attempts")

    freshness = _object(root.get("freshness"), "record.freshness", errors)
    freshness_keys = {"max_age_days", "material_dimensions"}
    _required_keys(freshness, freshness_keys, freshness_keys, "record.freshness", errors)
    _integer(freshness.get("max_age_days"), "record.freshness.max_age_days", errors, 1)
    dimensions = freshness.get("material_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        errors.append("record.freshness.material_dimensions must be a non-empty array")
    else:
        if len(set(str(item) for item in dimensions)) != len(dimensions):
            errors.append("record.freshness.material_dimensions must be unique")
        for dimension in dimensions:
            if dimension not in MATERIAL_DIMENSIONS:
                errors.append(f"unknown material dimension: {dimension}")
        missing_dimensions = MATERIAL_DIMENSIONS - set(dimensions)
        if missing_dimensions:
            errors.append(
                "record.freshness.material_dimensions missing required dimensions: "
                + ", ".join(sorted(missing_dimensions))
            )
    return errors


def _lookup(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


_MISSING = object()


def staleness_reasons(
    record: dict[str, Any], current_context: dict[str, Any], as_of: datetime
) -> list[str]:
    reasons: list[str] = []
    recorded_at = _timestamp(record.get("recorded_at"), "record.recorded_at", reasons)
    max_age = record.get("freshness", {}).get("max_age_days")
    if recorded_at is not None and isinstance(max_age, int):
        age_seconds = (as_of.astimezone(timezone.utc) - recorded_at).total_seconds()
        if age_seconds > max_age * 86400:
            reasons.append(f"evidence age exceeds {max_age} days")
    for dimension in record.get("freshness", {}).get("material_dimensions", []):
        recorded = _lookup(record, dimension)
        current = _lookup(current_context, dimension)
        if current is _MISSING:
            reasons.append(f"current context is missing {dimension}")
        elif recorded != current:
            reasons.append(f"material dimension changed: {dimension}")
    return reasons


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--current-context", type=Path)
    parser.add_argument("--as-of", help="ISO-8601 timestamp; defaults to now")
    parser.add_argument("--fail-if-stale", action="store_true")
    args = parser.parse_args(argv)
    try:
        record = load_json(args.record)
        errors = validate_record(record)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Evaluation cell valid: {record['cell_id']}")
        if args.current_context:
            context = load_json(args.current_context)
            as_of_errors: list[str] = []
            as_of = (
                _timestamp(args.as_of, "--as-of", as_of_errors)
                if args.as_of
                else datetime.now(timezone.utc)
            )
            if as_of_errors or as_of is None:
                for error in as_of_errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            reasons = staleness_reasons(record, context, as_of)
            if reasons:
                for reason in reasons:
                    print(f"STALE: {reason}")
                return 2 if args.fail_if_stale else 0
            print("Evaluation cell current for the supplied context.")
    except ValueError as exc:
        print(f"Evaluation cell validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
