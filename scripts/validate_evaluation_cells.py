#!/usr/bin/env python3
"""Validate retained matched evaluation-cell records as a repository ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import validate_evaluation_cell as cells


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CELLS = ROOT / "evaluation" / "harbor" / "results" / "cells"
DEFAULT_SUITES = ROOT / "evaluation" / "harbor" / "suites.json"


def _declared_tasks(manifest: dict[str, Any]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for suite in manifest.get("suites", []):
        skill = suite.get("skill")
        for task in suite.get("tasks", []):
            name = task.get("name")
            if isinstance(name, str) and isinstance(skill, str):
                owners[name] = skill
    return owners


def validate_ledger(cells_root: Path, suites_path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    try:
        manifest = json.loads(suites_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return 0, [f"cannot load suite manifest {suites_path}: {exc}"]
    owners = _declared_tasks(manifest)
    seen_ids: dict[str, Path] = {}
    paths = sorted(cells_root.glob("*.json")) if cells_root.is_dir() else []
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        record_errors = cells.validate_record(record)
        errors.extend(f"{path}: {error}" for error in record_errors)
        if not isinstance(record, dict):
            continue
        cell_id = record.get("cell_id")
        if isinstance(cell_id, str):
            if path.stem != cell_id:
                errors.append(f"{path}: filename must be {cell_id}.json")
            previous = seen_ids.get(cell_id)
            if previous:
                errors.append(f"{path}: duplicate cell_id {cell_id!r} (also {previous})")
            else:
                seen_ids[cell_id] = path
        scope = record.get("scope")
        if isinstance(scope, dict):
            task = scope.get("task")
            skill = scope.get("skill")
            if task not in owners:
                errors.append(f"{path}: task {task!r} is not declared in suites.json")
            elif owners[task] != skill:
                errors.append(
                    f"{path}: task {task!r} belongs to {owners[task]!r}, not {skill!r}"
                )
    return len(paths), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells-root", type=Path, default=DEFAULT_CELLS)
    parser.add_argument("--suites", type=Path, default=DEFAULT_SUITES)
    args = parser.parse_args(argv)
    count, errors = validate_ledger(args.cells_root, args.suites)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Evaluation-cell ledger valid: {count} retained record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
