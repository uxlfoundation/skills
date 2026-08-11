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
    triage_policy = policy["triage"]
    assert isinstance(triage_policy, dict)
    efficiency_policy = policy["efficiency"]
    assert isinstance(efficiency_policy, dict)
    required_workflow = set(triage_policy["required_workflow"])
    accepted_origins = set(triage_policy["accepted_origins"])
    target_environments = {
        "manual-gpu",
        "target-cpu",
        "target-gpu",
        "target-device",
        "target-distributed",
    }
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
        "- Comparison arms: " + ", ".join(f"`{item}`" for item in policy["comparison_arms"]),
        "- Full triage workflow: " + " -> ".join(f"`{item}`" for item in triage_policy["required_workflow"]),
        "- Accepted real-world origins: " + ", ".join(f"`{item}`" for item in triage_policy["accepted_origins"]),
        f"- Efficiency quality gate: `{efficiency_policy['quality_gate']}` at reward {efficiency_policy['verified_reward_floor']:.2f}",
        f"- Primary efficiency metric: `{efficiency_policy['primary_metric']}`",
        f"- Infrastructure failures: `{policy['infrastructure_failure_policy']}`",
        "- Promotion guardrails: maximum task mean regression {maximum_task_mean_regression:.2f}; maximum suite mean regression {maximum_suite_mean_regression:.2f}".format(**policy["promotion_thresholds"]),
        "",
        "## Coverage summary",
        "",
        "A real end-to-end task is implemented, reproduces live, performs every triage stage, and comes from a maintainer incident or upstream regression.",
        "",
        "| Skill | Target | Implemented | Live implemented | Fixture/review implemented | Target hardware | Real end-to-end | Planned |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for suite in suites:
        assert isinstance(suite, dict)
        tasks = suite["tasks"]
        assert isinstance(tasks, list)
        implemented = sum(task["status"] == "implemented" for task in tasks)
        live_implemented = sum(
            task["status"] == "implemented" and task["reproduction"] == "live"
            for task in tasks
        )
        fixture_implemented = sum(
            task["status"] == "implemented" and task["reproduction"] != "live"
            for task in tasks
        )
        target_hardware = sum(task["environment"] in target_environments for task in tasks)
        real_end_to_end = sum(
            task["status"] == "implemented"
            and task["reproduction"] == "live"
            and task["origin"] in accepted_origins
            and required_workflow.issubset(task["workflow"])
            for task in tasks
        )
        planned = sum(task["status"] == "planned" for task in tasks)
        lines.append(
            f"| `{suite['skill']}` | {suite['target_task_count']} | {implemented} | "
            f"{live_implemented} | {fixture_implemented} | {target_hardware} | "
            f"{real_end_to_end} | {planned} |"
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
                "| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for task in suite["tasks"]:
            covers = ", ".join(f"`{item}`" for item in task["covers"])
            workflow = " -> ".join(task["workflow"])
            lines.append(
                f"| `{task['name']}` | {task['status']} | {task['role']} | "
                f"{task['calibration']} | {task['track']} | {task['environment']} | "
                f"{task['reproduction']} | {task['origin']} | {workflow} | "
                f"{task['hardware']} | {covers} |"
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
