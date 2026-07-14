#!/usr/bin/env python3
"""Validate executable evaluator task fixtures and optionally run oracle verifiers."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "evaluation" / "tasks"
SCHEMA = ROOT / "schemas" / "executable-task.schema.json"
REQUIRED_TASK_KEYS = {
    "schema_version",
    "id",
    "skill",
    "track",
    "hardware_tier",
    "category",
    "prompt",
    "starter",
    "oracle",
    "verifier",
    "expected_artifacts",
    "timeout_seconds",
}
OPTIONAL_TASK_KEYS = {"notes"}
ALLOWED_TASK_KEYS = REQUIRED_TASK_KEYS | OPTIONAL_TASK_KEYS
ALLOWED_TRACKS = {"executable_tasks", "hardware_backend"}
ALLOWED_HARDWARE_TIERS = {"hosted_ci", "cpu_runner", "sycl_gpu_runner", "distributed_runner", "backend_specific_runner"}


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


def task_dirs() -> list[Path]:
    if not TASKS.exists():
        return []
    return sorted(path for path in TASKS.iterdir() if path.is_dir())


def validate_task(task_dir: Path) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    task_file = task_dir / "task.json"
    task, load_errors = load_json(task_file)
    errors.extend(load_errors)
    if errors:
        return None, errors

    missing = sorted(REQUIRED_TASK_KEYS.difference(task))
    if missing:
        errors.append(f"{task_file}: missing keys: {', '.join(missing)}")
    unknown = sorted(set(task).difference(ALLOWED_TASK_KEYS))
    if unknown:
        errors.append(f"{task_file}: unknown keys: {', '.join(unknown)}")
    if task.get("schema_version") != "0":
        errors.append(f"{task_file}: schema_version must be '0'")
    if task.get("id") != task_dir.name:
        errors.append(f"{task_file}: id must match task directory name")
    if task.get("track") not in ALLOWED_TRACKS:
        errors.append(f"{task_file}: invalid track {task.get('track')!r}")
    if task.get("hardware_tier") not in ALLOWED_HARDWARE_TIERS:
        errors.append(f"{task_file}: invalid hardware_tier {task.get('hardware_tier')!r}")
    if not isinstance(task.get("timeout_seconds"), int) or task.get("timeout_seconds", 0) < 1:
        errors.append(f"{task_file}: timeout_seconds must be a positive integer")
    if not isinstance(task.get("expected_artifacts"), list) or not task.get("expected_artifacts"):
        errors.append(f"{task_file}: expected_artifacts must be a non-empty list")
    if any(not isinstance(task.get(key), str) or not task.get(key) for key in ("skill", "category", "prompt")):
        errors.append(f"{task_file}: skill, category, and prompt must be non-empty strings")

    starter = task_dir / str(task.get("starter", "starter"))
    oracle = task_dir / str(task.get("oracle", "oracle"))
    verifier = task_dir / str(task.get("verifier", "verify.py"))
    for label, path in (("starter", starter), ("oracle", oracle), ("verifier", verifier)):
        if not path.exists():
            errors.append(f"{task_file}: missing {label}: {path.relative_to(task_dir)}")
    if verifier.exists() and not verifier.is_file():
        errors.append(f"{task_file}: verifier must be a file")

    if oracle.exists() and isinstance(task.get("expected_artifacts"), list):
        for artifact in task["expected_artifacts"]:
            if not isinstance(artifact, str) or not artifact:
                errors.append(f"{task_file}: expected artifact entries must be strings")
                continue
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{task_file}: expected artifact must stay under oracle: {artifact}")
                continue
            if not (oracle / artifact).exists():
                errors.append(f"{task_file}: oracle missing expected artifact {artifact}")

    return task, errors


def copy_tree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True)
        else:
            shutil.copy2(child, target)


def run_oracle(task_dir: Path, task: dict) -> tuple[int, str]:
    starter = task_dir / task["starter"]
    oracle = task_dir / task["oracle"]
    verifier = task_dir / task["verifier"]
    with tempfile.TemporaryDirectory(prefix=f"uxl-task-{task['id']}-") as tmp:
        workspace = Path(tmp) / "workspace"
        copy_tree_contents(starter, workspace)
        copy_tree_contents(oracle, workspace)
        command = [sys.executable, str(verifier), str(workspace)]
        completed = subprocess.run(
            command,
            cwd=task_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=int(task["timeout_seconds"]),
            check=False,
        )
        return completed.returncode, completed.stdout


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-oracles", action="store_true", help="Run verifier against each oracle solution.")
    parser.add_argument("--task", action="append", help="Only validate selected task id(s).")
    args = parser.parse_args(argv)

    errors: list[str] = []
    schema, schema_errors = load_json(SCHEMA)
    errors.extend(schema_errors)
    if schema and schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{SCHEMA}: expected draft 2020-12 $schema")

    selected = set(args.task or [])
    dirs = task_dirs()
    if selected:
        dirs = [path for path in dirs if path.name in selected]
        missing = selected.difference({path.name for path in dirs})
        for task_id in sorted(missing):
            errors.append(f"{TASKS}: requested task not found: {task_id}")
    if not dirs:
        errors.append(f"{TASKS}: no executable tasks found")

    valid_tasks: list[tuple[Path, dict]] = []
    for task_dir in dirs:
        task, task_errors = validate_task(task_dir)
        errors.extend(task_errors)
        if task and not task_errors:
            valid_tasks.append((task_dir, task))

    if errors:
        print("Executable task validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.run_oracles:
        for task_dir, task in valid_tasks:
            code, output = run_oracle(task_dir, task)
            if code != 0:
                print(f"Oracle verifier failed for {task['id']}:")
                print(output)
                return code
            print(f"Oracle verifier passed for {task['id']}.")

    print(f"Executable task validation passed: {len(valid_tasks)} task(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
