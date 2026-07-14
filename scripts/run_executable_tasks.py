#!/usr/bin/env python3
"""Run executable UXL evaluator tasks against candidate solution directories."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from validate_executable_tasks import copy_tree_contents, task_dirs, validate_task


def parse_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    selected: set[str] = set()
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                selected.add(item)
    return selected or None


def load_tasks(task_filter: set[str] | None) -> tuple[list[tuple[Path, dict]], list[str]]:
    dirs = task_dirs()
    if task_filter is not None:
        dirs = [path for path in dirs if path.name in task_filter]

    errors: list[str] = []
    selected = {path.name for path in dirs}
    if task_filter is not None:
        for task_id in sorted(task_filter.difference(selected)):
            errors.append(f"evaluation/tasks: requested task not found: {task_id}")

    tasks: list[tuple[Path, dict]] = []
    for task_dir in dirs:
        task, task_errors = validate_task(task_dir)
        errors.extend(task_errors)
        if task and not task_errors:
            tasks.append((task_dir, task))
    if not tasks and not errors:
        errors.append("evaluation/tasks: no executable tasks found")
    return tasks, errors


def candidate_path(candidate_dir: Path, task: dict) -> Path | None:
    task_id = task["id"]
    skill = task["skill"]
    candidates = [
        candidate_dir / task_id,
        candidate_dir / skill / task_id,
        candidate_dir / f"{skill}--{task_id}",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def compact_output(text: str, limit: int = 320) -> str:
    value = " / ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(value) > limit:
        return value[: limit - 3] + "..."
    return value or "no verifier output"


def run_candidate(task_dir: Path, task: dict, candidate_dir: Path) -> dict:
    candidate = candidate_path(candidate_dir, task)
    if candidate is None:
        return {
            "task": task["id"],
            "skill": task["skill"],
            "candidate_path": None,
            "score": 0.0,
            "passed": False,
            "missing": True,
            "notes": ["missing candidate"],
            "verifier_output": "",
        }
    if not candidate.is_dir():
        return {
            "task": task["id"],
            "skill": task["skill"],
            "candidate_path": str(candidate),
            "score": 0.0,
            "passed": False,
            "missing": False,
            "notes": ["candidate path is not a directory"],
            "verifier_output": "",
        }

    starter = task_dir / task["starter"]
    verifier = task_dir / task["verifier"]
    with tempfile.TemporaryDirectory(prefix=f"uxl-task-{task['id']}-") as tmp:
        workspace = Path(tmp) / "workspace"
        copy_tree_contents(starter, workspace)
        copy_tree_contents(candidate, workspace)

        missing_artifacts = [artifact for artifact in task["expected_artifacts"] if not (workspace / artifact).exists()]
        if missing_artifacts:
            return {
                "task": task["id"],
                "skill": task["skill"],
                "candidate_path": str(candidate),
                "score": 0.0,
                "passed": False,
                "missing": False,
                "notes": [f"missing artifact: {artifact}" for artifact in missing_artifacts],
                "verifier_output": "",
            }

        completed = subprocess.run(
            [sys.executable, str(verifier), str(workspace)],
            cwd=task_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=int(task["timeout_seconds"]),
            check=False,
        )

    passed = completed.returncode == 0
    notes = ["pass"] if passed else [compact_output(completed.stdout)]
    return {
        "task": task["id"],
        "skill": task["skill"],
        "candidate_path": str(candidate),
        "score": 1.0 if passed else 0.0,
        "passed": passed,
        "missing": False,
        "notes": notes,
        "verifier_output": completed.stdout,
    }


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_report(tasks: list[tuple[Path, dict]], candidate_dir: Path, label: str) -> dict:
    cases = [run_candidate(task_dir, task, candidate_dir) for task_dir, task in tasks]
    by_skill: dict[str, list[dict]] = {}
    for case in cases:
        by_skill.setdefault(case["skill"], []).append(case)

    skills = []
    for skill, items in sorted(by_skill.items()):
        scores = [item["score"] for item in items]
        skills.append(
            {
                "skill": skill,
                "tasks": len(items),
                "passed": sum(1 for item in items if item["passed"]),
                "missing_candidates": sum(1 for item in items if item["missing"]),
                "average": round(average(scores), 4),
            }
        )

    scores = [case["score"] for case in cases]
    summary = {
        "label": label,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "task_count": len(cases),
        "skill_count": len(skills),
        "passed": sum(1 for case in cases if case["passed"]),
        "missing_candidates": sum(1 for case in cases if case["missing"]),
        "average": round(average(scores), 4),
    }
    return {
        "schema_version": "0",
        "label": label,
        "candidate_dir": str(candidate_dir),
        "summary": summary,
        "skills": skills,
        "cases": cases,
    }


def escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def markdown_report(report: dict) -> str:
    summary = report["summary"]
    lines = [
        f"# UXL Executable Task Scorecard: {summary['label']}",
        "",
        "## Summary",
        "",
        "| Tasks | Skills | Passed | Missing candidates | Average |",
        "| ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {summary['task_count']} | {summary['skill_count']} | {summary['passed']} | "
            f"{summary['missing_candidates']} | {summary['average']:.4f} |"
        ),
        "",
        "## By Skill",
        "",
        "| Skill | Tasks | Passed | Missing candidates | Average |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for skill in report["skills"]:
        lines.append(
            f"| `{skill['skill']}` | {skill['tasks']} | {skill['passed']} | "
            f"{skill['missing_candidates']} | {skill['average']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Tasks",
            "",
            "| Skill | Task | Score | Notes |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for case in report["cases"]:
        notes = escape_table("; ".join(case["notes"]))
        lines.append(f"| `{case['skill']}` | `{case['task']}` | {case['score']:.4f} | {notes} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True, help="Directory containing task candidate outputs.")
    parser.add_argument("--output-dir", type=Path, help="Directory for executable-scorecard.json and .md.")
    parser.add_argument("--label", default="manual", help="Human-readable report label.")
    parser.add_argument("--task", action="append", help="Task id filter. May be repeated or comma-separated.")
    parser.add_argument("--skill", action="append", help="Skill filter. May be repeated or comma-separated.")
    parser.add_argument("--allow-missing", action="store_true", help="Do not fail when candidate task dirs are missing.")
    parser.add_argument("--fail-under-pass-rate", type=float, help="Minimum executable task pass rate.")
    args = parser.parse_args(argv)

    tasks, errors = load_tasks(parse_filter(args.task))
    if errors:
        print("Executable task loading failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill_filter = parse_filter(args.skill)
    if skill_filter is not None:
        tasks = [(task_dir, task) for task_dir, task in tasks if task["skill"] in skill_filter]
        missing_skills = sorted(skill_filter.difference({task["skill"] for _, task in tasks}))
        if missing_skills:
            print(f"No executable tasks found for skills: {', '.join(missing_skills)}", file=sys.stderr)
            return 1

    if not tasks:
        print("No executable tasks selected.", file=sys.stderr)
        return 1

    report = build_report(tasks, args.candidate_dir, args.label)
    markdown = markdown_report(report)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "executable-scorecard.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "executable-scorecard.md").write_text(markdown, encoding="utf-8")

    print(markdown)

    summary = report["summary"]
    failed = False
    if summary["missing_candidates"] and not args.allow_missing:
        print("Missing candidate task directories detected. Use --allow-missing for exploratory reports.", file=sys.stderr)
        failed = True
    if args.fail_under_pass_rate is not None and summary["average"] < args.fail_under_pass_rate:
        print(
            f"Executable pass rate {summary['average']:.4f} is below {args.fail_under_pass_rate:.4f}.",
            file=sys.stderr,
        )
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
