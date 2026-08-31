#!/usr/bin/env python3
"""Validate the public ledger of sanitized specialized-target qualifications."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import validate_target_qualification as qualification


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "evaluation" / "harbor" / "results" / "qualifications"
DEFAULT_SUITES = ROOT / "evaluation" / "harbor" / "suites.json"


def _declared_tasks(manifest: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    tasks: dict[str, tuple[str, dict[str, Any]]] = {}
    for suite in manifest.get("suites", []):
        skill = suite.get("skill")
        for task in suite.get("tasks", []):
            name = task.get("name")
            if isinstance(name, str) and isinstance(skill, str) and isinstance(task, dict):
                tasks[name] = (skill, task)
    return tasks


def validate_ledger(records_root: Path, suites_path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    try:
        manifest = json.loads(suites_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return 0, [f"cannot load suite manifest {suites_path}: {exc}"]
    declared = _declared_tasks(manifest)
    seen: dict[str, Path] = {}
    paths = sorted(records_root.glob("*.json")) if records_root.is_dir() else []
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        errors.extend(f"{path}: {error}" for error in qualification.validate_record(record))
        if not isinstance(record, dict):
            continue
        record_id = record.get("qualification_id")
        if isinstance(record_id, str):
            if path.stem != record_id:
                errors.append(f"{path}: filename must be {record_id}.json")
            if record_id in seen:
                errors.append(f"{path}: duplicate qualification_id {record_id!r} (also {seen[record_id]})")
            else:
                seen[record_id] = path
        scope = record.get("scope")
        lane = record.get("lane")
        if not isinstance(scope, dict) or not isinstance(lane, dict):
            continue
        task_name = scope.get("task")
        if task_name not in declared:
            errors.append(f"{path}: task {task_name!r} is not declared in suites.json")
            continue
        skill, task = declared[task_name]
        if scope.get("skill") != skill:
            errors.append(f"{path}: task {task_name!r} belongs to {skill!r}, not {scope.get('skill')!r}")
        if task.get("status") != "implemented":
            errors.append(f"{path}: qualification task {task_name!r} must be implemented")
        if lane.get("environment") != task.get("environment"):
            errors.append(f"{path}: lane environment must match task environment {task.get('environment')!r}")
        if lane.get("hardware_class") != task.get("hardware"):
            errors.append(f"{path}: lane hardware_class must match task hardware {task.get('hardware')!r}")
    return len(paths), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-root", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--suites", type=Path, default=DEFAULT_SUITES)
    args = parser.parse_args(argv)
    count, errors = validate_ledger(args.records_root, args.suites)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Target-qualification ledger valid: {count} retained record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
