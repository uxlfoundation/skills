#!/usr/bin/env python3
"""Qualify a specialized target from reviewed config, then run its Harbor oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_ROOT))
import check_harbor_job  # noqa: E402


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
ENV_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HARDWARE_CLASSES = {"target-cpu", "target-gpu", "target-device", "target-distributed"}
SECRET_NAME_RE = re.compile(r"(?:TOKEN|SECRET|PASSWORD|PASSWD|AUTH|CREDENTIAL|PRIVATE|API_KEY)", re.I)


def _object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _exact_keys(
    value: dict[str, Any], required: set[str], path: str, errors: list[str]
) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing:
        errors.append(f"{path} missing: {', '.join(missing)}")
    if extra:
        errors.append(f"{path} has unknown fields: {', '.join(extra)}")


def _string_list(value: Any, path: str, errors: list[str], *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        errors.append(f"{path} must be {'an' if allow_empty else 'a non-empty'} array of strings")
        return []
    if not all(isinstance(item, str) and item for item in value):
        errors.append(f"{path} must contain only non-empty strings")
        return []
    return value


def validate_adapter(config: Any) -> list[str]:
    errors: list[str] = []
    root = _object(config, "adapter", errors)
    root_keys = {"schema_version", "adapter_id", "task", "runner", "probes", "harbor"}
    _exact_keys(root, root_keys, "adapter", errors)
    if root.get("schema_version") != "1.0":
        errors.append("adapter.schema_version must be '1.0'")
    adapter_id = root.get("adapter_id")
    if not isinstance(adapter_id, str) or not NAME_RE.fullmatch(adapter_id):
        errors.append("adapter.adapter_id must be lowercase kebab-case")

    task = _object(root.get("task"), "adapter.task", errors)
    task_keys = {"skill", "name", "hardware_class"}
    _exact_keys(task, task_keys, "adapter.task", errors)
    for key in ("skill", "name"):
        value = task.get(key)
        if not isinstance(value, str) or not NAME_RE.fullmatch(value):
            errors.append(f"adapter.task.{key} must be lowercase kebab-case")
    if task.get("hardware_class") not in HARDWARE_CLASSES:
        errors.append(f"adapter.task.hardware_class must be one of {sorted(HARDWARE_CLASSES)}")

    runner = _object(root.get("runner"), "adapter.runner", errors)
    _exact_keys(runner, {"required_labels"}, "adapter.runner", errors)
    labels = _string_list(
        runner.get("required_labels"), "adapter.runner.required_labels", errors, allow_empty=False
    )
    if len(labels) != len(set(labels)):
        errors.append("adapter.runner.required_labels must be unique")
    for label in labels:
        if not NAME_RE.fullmatch(label):
            errors.append(f"adapter runner label must be lowercase kebab-case: {label!r}")

    probes = root.get("probes")
    if not isinstance(probes, list) or not probes:
        errors.append("adapter.probes must be a non-empty array")
        probes = []
    seen_probe_ids: set[str] = set()
    for index, raw_probe in enumerate(probes):
        path = f"adapter.probes[{index}]"
        probe = _object(raw_probe, path, errors)
        probe_keys = {"id", "command", "timeout_seconds", "required_patterns", "publish_output"}
        _exact_keys(probe, probe_keys, path, errors)
        probe_id = probe.get("id")
        if not isinstance(probe_id, str) or not NAME_RE.fullmatch(probe_id):
            errors.append(f"{path}.id must be lowercase kebab-case")
        elif probe_id in seen_probe_ids:
            errors.append(f"duplicate probe id: {probe_id}")
        else:
            seen_probe_ids.add(probe_id)
        _string_list(probe.get("command"), f"{path}.command", errors, allow_empty=False)
        _string_list(
            probe.get("required_patterns"),
            f"{path}.required_patterns",
            errors,
            allow_empty=True,
        )
        timeout = probe.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 600:
            errors.append(f"{path}.timeout_seconds must be an integer from 1 through 600")
        if not isinstance(probe.get("publish_output"), bool):
            errors.append(f"{path}.publish_output must be boolean")

    harbor = _object(root.get("harbor"), "adapter.harbor", errors)
    harbor_keys = {"command", "timeout_seconds", "environment"}
    _exact_keys(harbor, harbor_keys, "adapter.harbor", errors)
    _string_list(harbor.get("command"), "adapter.harbor.command", errors, allow_empty=False)
    timeout = harbor.get("timeout_seconds")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 86400:
        errors.append("adapter.harbor.timeout_seconds must be an integer from 1 through 86400")
    environment = _object(harbor.get("environment"), "adapter.harbor.environment", errors)
    for name, value in environment.items():
        if not isinstance(name, str) or not ENV_RE.fullmatch(name):
            errors.append(f"invalid Harbor environment variable name: {name!r}")
        if SECRET_NAME_RE.search(str(name)):
            errors.append(f"secrets are not allowed in adapter configuration: {name!r}")
        if not isinstance(value, str):
            errors.append(f"adapter.harbor.environment.{name} must be a string")
    return errors


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run_probe(
    probe: dict[str, Any],
    cwd: Path,
    environment: dict[str, str],
    private_log: Path | None = None,
) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    try:
        completed = subprocess.run(
            probe["command"],
            cwd=cwd,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=probe["timeout_seconds"],
            check=False,
        )
        output = completed.stdout
        if private_log is not None:
            private_log.parent.mkdir(parents=True, exist_ok=True)
            private_log.write_text(output, encoding="utf-8")
        missing = [pattern for pattern in probe["required_patterns"] if pattern not in output]
        record: dict[str, Any] = {
            "id": probe["id"],
            "command": probe["command"],
            "return_code": completed.returncode,
            "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 3),
            "output_sha256": sha256_bytes(output.encode("utf-8")),
            "required_patterns_present": not missing,
            "passed": completed.returncode == 0 and not missing,
        }
        if probe["publish_output"]:
            record["output"] = output[:16000]
        if missing:
            record["missing_patterns"] = missing
        return record
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        if private_log is not None:
            private_log.parent.mkdir(parents=True, exist_ok=True)
            private_log.write_text(output, encoding="utf-8")
        return {
            "id": probe["id"],
            "command": probe["command"],
            "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 3),
            "output_sha256": sha256_bytes(output.encode("utf-8")),
            "timed_out": True,
            "passed": False,
        }
    except OSError as exc:
        message = f"{type(exc).__name__}: {exc}"
        if private_log is not None:
            private_log.parent.mkdir(parents=True, exist_ok=True)
            private_log.write_text(message + "\n", encoding="utf-8")
        return {
            "id": probe["id"],
            "command": probe["command"],
            "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 3),
            "output_sha256": sha256_bytes(message.encode("utf-8")),
            "error": message,
            "passed": False,
        }


def command_version(command: list[str], cwd: Path, environment: dict[str, str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [*command, "--version"],
            cwd=cwd,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        output = completed.stdout.strip()
        return {
            "command": command,
            "return_code": completed.returncode,
            "version": output[:1000] if output else "unreported",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "error": f"{type(exc).__name__}: {exc}"}


def declared_task(source_root: Path, task_name: str) -> tuple[str, dict[str, Any]] | None:
    manifest_path = source_root / "evaluation" / "harbor" / "suites.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for suite in manifest.get("suites", []):
        for task in suite.get("tasks", []):
            if task.get("name") == task_name:
                return suite.get("skill"), task
    return None


def build_harbor_command(
    config: dict[str, Any], source_root: Path, jobs_root: Path, job_name: str
) -> list[str]:
    return [
        *config["harbor"]["command"],
        "run",
        "--path",
        str(source_root / "evaluation" / "harbor" / "tasks"),
        "--include-task-name",
        config["task"]["name"],
        "--agent",
        "oracle",
        "--n-attempts",
        "1",
        "--job-name",
        job_name,
        "--jobs-dir",
        str(jobs_root),
        "--n-concurrent",
        "1",
        "--yes",
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(path: Path, *, adapter_id: str, commit: str, task: str, status: str, detail: str) -> None:
    path.write_text(
        "\n".join(
            [
                "# Specialized target qualification",
                "",
                f"- Adapter: `{adapter_id}`",
                f"- Evaluator commit: `{commit}`",
                f"- Oracle task: `{task}`",
                f"- Status: **{status}**",
                f"- Detail: {detail}",
                "",
                "A passing oracle qualifies this execution lane. It does not prove skill benefit.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        config_bytes = args.config.read_bytes()
        config = json.loads(config_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot load adapter configuration: {exc}", file=sys.stderr)
        return 2
    errors = validate_adapter(config)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    if args.validate_only:
        print(f"Target adapter valid: {config['adapter_id']}")
        return 0
    if not COMMIT_RE.fullmatch(args.expected_commit):
        print("--expected-commit must be a full 40-character Git commit SHA", file=sys.stderr)
        return 2

    source_root = args.source_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary_path = output / "qualification-summary.md"
    provenance_path = output / "runner-provenance.json"
    try:
        actual_commit = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip().lower()
        if actual_commit != args.expected_commit.lower():
            raise ValueError(
                f"checked-out evaluator commit {actual_commit} does not match {args.expected_commit.lower()}"
            )
        task_entry = declared_task(source_root, config["task"]["name"])
        if not task_entry:
            raise ValueError(f"task is not declared: {config['task']['name']}")
        declared_skill, task = task_entry
        if declared_skill != config["task"]["skill"]:
            raise ValueError(f"task belongs to {declared_skill}, not {config['task']['skill']}")
        if task.get("hardware") != config["task"]["hardware_class"]:
            raise ValueError(
                f"task hardware is {task.get('hardware')}, not {config['task']['hardware_class']}"
            )

        environment = os.environ.copy()
        environment.update(config["harbor"]["environment"])
        provenance: dict[str, Any] = {
            "schema_version": "1.0",
            "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "adapter_id": config["adapter_id"],
            "adapter_config_sha256": sha256_bytes(config_bytes),
            "source_commit": actual_commit,
            "task": config["task"],
            "runner": {
                "name": os.environ.get("RUNNER_NAME", "unreported"),
                "os": platform.platform(),
                "architecture": platform.machine(),
                "required_labels": config["runner"]["required_labels"],
            },
            "toolchain": {
                "python": platform.python_version(),
                "harbor": command_version(config["harbor"]["command"], source_root, environment),
            },
            "probes": [],
            "oracle": {"status": "not-run"},
        }
        for probe in config["probes"]:
            record = run_probe(
                probe,
                source_root,
                environment,
                output / "probe-logs" / f"{probe['id']}.log",
            )
            provenance["probes"].append(record)
            write_json(provenance_path, provenance)
            if not record["passed"]:
                write_summary(
                    summary_path,
                    adapter_id=config["adapter_id"],
                    commit=actual_commit,
                    task=config["task"]["name"],
                    status="FAILED",
                    detail=f"required probe {probe['id']} failed",
                )
                return 1

        jobs_root = output / "harbor-jobs"
        job_name = f"{config['adapter_id']}-{actual_commit[:12]}-oracle"
        command = build_harbor_command(config, source_root, jobs_root, job_name)
        completed = subprocess.run(
            command,
            cwd=source_root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=config["harbor"]["timeout_seconds"],
            check=False,
        )
        (output / "oracle.log").write_text(completed.stdout, encoding="utf-8")
        result_path = jobs_root / job_name / "result.json"
        oracle_errors: list[str] = []
        if completed.returncode != 0:
            oracle_errors.append(f"Harbor exited with {completed.returncode}")
        if not result_path.is_file():
            oracle_errors.append("Harbor result.json was not produced")
        else:
            result = check_harbor_job.load_result(result_path)
            oracle_errors.extend(check_harbor_job.validate_result(result, 1, 1.0))
        provenance["oracle"] = {
            "status": "failed" if oracle_errors else "passed",
            "job_name": job_name,
            "result_path": str(result_path.relative_to(output)).replace("\\", "/"),
            "errors": oracle_errors,
        }
        write_json(provenance_path, provenance)
        status = "FAILED" if oracle_errors else "PASSED"
        detail = "; ".join(oracle_errors) if oracle_errors else "all host probes and the reward-1.0 oracle passed"
        write_summary(
            summary_path,
            adapter_id=config["adapter_id"],
            commit=actual_commit,
            task=config["task"]["name"],
            status=status,
            detail=detail,
        )
        print(detail)
        return 1 if oracle_errors else 0
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        write_summary(
            summary_path,
            adapter_id=config["adapter_id"],
            commit=args.expected_commit.lower(),
            task=config["task"]["name"],
            status="FAILED",
            detail=str(exc),
        )
        print(f"Target qualification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
