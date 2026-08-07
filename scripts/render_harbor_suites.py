#!/usr/bin/env python3
"""Render the Harbor suite manifest as a human-readable capability matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evaluation" / "harbor" / "suites.json"
DEFAULT_OUTPUT = ROOT / "evaluation" / "harbor" / "CAPABILITY_MATRIX.md"


def render(data: dict[str, object]) -> str:
    policy = data["policy"]
    assert isinstance(policy, dict)
    suites = data["suites"]
    assert isinstance(suites, list)
    lines = [
        "# Harbor capability matrix",
        "",
        "This file is generated from `evaluation/harbor/suites.json`. Do not edit it by hand.",
        "",
        "## Portfolio policy",
        "",
        f"- Minimum tasks per skill: {policy['minimum_tasks_per_skill']}",
        f"- Minimum discriminating tasks per skill: {policy['minimum_discriminating_tasks_per_skill']}",
        "- Required classes: " + ", ".join(f"`{item}`" for item in policy["required_capability_classes"]),
        "- Attempts: development {development_probe}, calibration {calibration}, promotion {promotion}".format(**policy["attempts"]),
        "- Promotion guardrails: maximum task mean regression {maximum_task_mean_regression:.2f}; maximum suite mean regression {maximum_suite_mean_regression:.2f}".format(**policy["promotion_thresholds"]),
        "",
        "## Coverage summary",
        "",
        "| Skill | Target | Implemented | Headroom | Ceiling | Planned |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for suite in suites:
        assert isinstance(suite, dict)
        tasks = suite["tasks"]
        assert isinstance(tasks, list)
        implemented = sum(task["status"] == "implemented" for task in tasks)
        headroom = sum(task["calibration"] == "headroom" for task in tasks)
        ceiling = sum(task["calibration"] == "ceiling" for task in tasks)
        planned = sum(task["status"] == "planned" for task in tasks)
        lines.append(
            f"| `{suite['skill']}` | {suite['target_task_count']} | {implemented} | "
            f"{headroom} | {ceiling} | {planned} |"
        )

    for suite in suites:
        assert isinstance(suite, dict)
        lines.extend(["", f"## {suite['skill']} ({suite['owner_project']})", "", "### Capabilities", ""])
        for capability in suite["capabilities"]:
            lines.append(
                f"- `{capability['id']}` ({capability['class']}): {capability['description']}"
            )
        lines.extend(
            [
                "",
                "### Task portfolio",
                "",
                "| Task | Status | Role | Calibration | Track | Environment | Covers |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for task in suite["tasks"]:
            covers = ", ".join(f"`{item}`" for item in task["covers"])
            lines.append(
                f"| `{task['name']}` | {task['status']} | {task['role']} | "
                f"{task['calibration']} | {task['track']} | {task['environment']} | {covers} |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = render(data)
    if args.check:
        actual = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if actual != expected:
            print(f"Harbor capability matrix is stale: {args.output}")
            return 1
        print("Harbor capability matrix is current.")
        return 0
    args.output.write_text(expected, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
