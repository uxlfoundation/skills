#!/usr/bin/env python3
"""Validate one sanitized specialized-target qualification record."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ENVIRONMENTS = {"manual-gpu", "target-cpu", "target-gpu", "target-device", "target-distributed"}
HARDWARE_CLASSES = {"target-cpu", "target-gpu", "target-device", "target-distributed"}


def _object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _exact(value: dict[str, Any], keys: set[str], path: str, errors: list[str]) -> None:
    for name in sorted(keys - set(value)):
        errors.append(f"{path}.{name} is required")
    for name in sorted(set(value) - keys):
        errors.append(f"{path}.{name} is not allowed")


def _text(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def _name(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not NAME_RE.fullmatch(value):
        errors.append(f"{path} must be a lowercase kebab-case name")


def _sha256(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{path} must be a lowercase SHA-256 digest")


def _positive_integer(value: Any, path: str, errors: list[str], maximum: int | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        errors.append(f"{path} must be a positive integer")
    elif maximum is not None and value > maximum:
        errors.append(f"{path} must be <= {maximum}")


def validate_record(record: Any) -> list[str]:
    errors: list[str] = []
    root = _object(record, "record", errors)
    root_keys = {"schema_version", "qualification_id", "recorded_at", "status", "scope", "lane", "evidence", "freshness", "limitations"}
    _exact(root, root_keys, "record", errors)
    if root.get("schema_version") != "1.0":
        errors.append("record.schema_version must be '1.0'")
    _name(root.get("qualification_id"), "record.qualification_id", errors)
    if root.get("status") != "passed":
        errors.append("record.status must be 'passed'")
    recorded_at = root.get("recorded_at")
    if not isinstance(recorded_at, str):
        errors.append("record.recorded_at must be an ISO-8601 timestamp with timezone")
    else:
        try:
            parsed = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError
        except ValueError:
            errors.append("record.recorded_at must be an ISO-8601 timestamp with timezone")

    scope = _object(root.get("scope"), "record.scope", errors)
    scope_keys = {"skill", "task", "task_revision", "verifier_sha256"}
    _exact(scope, scope_keys, "record.scope", errors)
    _name(scope.get("skill"), "record.scope.skill", errors)
    _name(scope.get("task"), "record.scope.task", errors)
    revision = _object(scope.get("task_revision"), "record.scope.task_revision", errors)
    revision_keys = {"repository", "commit", "content_sha256"}
    _exact(revision, revision_keys, "record.scope.task_revision", errors)
    _text(revision.get("repository"), "record.scope.task_revision.repository", errors)
    commit = revision.get("commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        errors.append("record.scope.task_revision.commit must be a lowercase 40-character Git SHA")
    _sha256(revision.get("content_sha256"), "record.scope.task_revision.content_sha256", errors)
    _sha256(scope.get("verifier_sha256"), "record.scope.verifier_sha256", errors)

    lane = _object(root.get("lane"), "record.lane", errors)
    lane_keys = {"lane_id", "adapter_id", "display_name", "environment", "hardware_class", "vendor", "device", "interface", "os", "architecture", "control"}
    _exact(lane, lane_keys, "record.lane", errors)
    for name in ("lane_id", "adapter_id"):
        _name(lane.get(name), f"record.lane.{name}", errors)
    for name in ("display_name", "vendor", "device", "interface", "os", "architecture"):
        _text(lane.get(name), f"record.lane.{name}", errors)
    if lane.get("environment") not in ENVIRONMENTS:
        errors.append("record.lane.environment is not a specialized environment")
    if lane.get("hardware_class") not in HARDWARE_CLASSES:
        errors.append("record.lane.hardware_class is not supported")
    if lane.get("control") not in {"access-controlled", "public"}:
        errors.append("record.lane.control must be access-controlled or public")

    evidence = _object(root.get("evidence"), "record.evidence", errors)
    evidence_keys = {"agent", "attempts", "completed_attempts", "errored_attempts", "reward", "result_sha256", "provenance_sha256", "workflow"}
    _exact(evidence, evidence_keys, "record.evidence", errors)
    if evidence.get("agent") != "oracle":
        errors.append("record.evidence.agent must be 'oracle'")
    for name in ("attempts", "completed_attempts"):
        _positive_integer(evidence.get(name), f"record.evidence.{name}", errors)
    if evidence.get("completed_attempts") != evidence.get("attempts"):
        errors.append("record.evidence.completed_attempts must equal attempts")
    if evidence.get("errored_attempts") != 0:
        errors.append("record.evidence.errored_attempts must be zero")
    if evidence.get("reward") != 1.0 or isinstance(evidence.get("reward"), bool):
        errors.append("record.evidence.reward must be 1.0")
    for name in ("result_sha256", "provenance_sha256"):
        _sha256(evidence.get(name), f"record.evidence.{name}", errors)
    workflow = _object(evidence.get("workflow"), "record.evidence.workflow", errors)
    _exact(workflow, {"visibility", "run_id"}, "record.evidence.workflow", errors)
    if workflow.get("visibility") not in {"public", "access-controlled", "local"}:
        errors.append("record.evidence.workflow.visibility is not supported")
    run_id = workflow.get("run_id")
    if run_id is not None and (not isinstance(run_id, str) or not run_id.isdigit()):
        errors.append("record.evidence.workflow.run_id must be null or digits")

    freshness = _object(root.get("freshness"), "record.freshness", errors)
    _exact(freshness, {"max_age_days"}, "record.freshness", errors)
    _positive_integer(freshness.get("max_age_days"), "record.freshness.max_age_days", errors, 365)
    limitations = root.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        errors.append("record.limitations must be a non-empty array")
    elif len(set(str(item) for item in limitations)) != len(limitations):
        errors.append("record.limitations must be unique")
    else:
        for index, limitation in enumerate(limitations):
            _text(limitation, f"record.limitations[{index}]", errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Target qualification validation failed: {exc}", file=sys.stderr)
        return 1
    errors = validate_record(record)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Target qualification valid: {record['qualification_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
