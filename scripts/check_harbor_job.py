#!/usr/bin/env python3
"""Fail CI when a Harbor job is incomplete, errored, or below its reward floor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_result(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Harbor result does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Harbor result is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Harbor result must be a JSON object: {path}")
    return data


def validate_result(
    result: dict[str, Any], expected_trials: int, reward_floor: float
) -> list[str]:
    errors: list[str] = []
    stats = result.get("stats")
    if not isinstance(stats, dict):
        return ["result.stats is missing or is not an object"]

    total = result.get("n_total_trials")
    completed = stats.get("n_completed_trials")
    if total != expected_trials:
        errors.append(f"expected {expected_trials} total trials, found {total!r}")
    if completed != expected_trials:
        errors.append(f"expected {expected_trials} completed trials, found {completed!r}")

    for field in (
        "n_errored_trials",
        "n_running_trials",
        "n_pending_trials",
        "n_cancelled_trials",
    ):
        value = stats.get(field)
        if value != 0:
            errors.append(f"expected stats.{field}=0, found {value!r}")

    if not result.get("finished_at"):
        errors.append("job has no finished_at timestamp")

    evals = stats.get("evals")
    if not isinstance(evals, dict) or not evals:
        errors.append("job has no evaluation statistics")
        return errors

    evaluated_trials = 0
    for eval_name, eval_stats in evals.items():
        if not isinstance(eval_stats, dict):
            errors.append(f"evaluation {eval_name!r} has invalid statistics")
            continue
        n_trials = eval_stats.get("n_trials")
        if isinstance(n_trials, int):
            evaluated_trials += n_trials
        else:
            errors.append(f"evaluation {eval_name!r} has invalid n_trials {n_trials!r}")
        if eval_stats.get("n_errors") != 0:
            errors.append(
                f"evaluation {eval_name!r} has {eval_stats.get('n_errors')!r} errors"
            )
        metrics = eval_stats.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            errors.append(f"evaluation {eval_name!r} has no metrics")
            continue
        for index, metric in enumerate(metrics):
            reward = None
            if isinstance(metric, dict):
                reward = metric.get("reward", metric.get("mean"))
            if not isinstance(reward, (int, float)) or reward < reward_floor:
                errors.append(
                    f"evaluation {eval_name!r} metric {index} reward {reward!r} "
                    f"is below {reward_floor}"
                )

    if evaluated_trials != expected_trials:
        errors.append(
            f"expected {expected_trials} evaluated trials, found {evaluated_trials}"
        )

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="Path to a Harbor job result.json")
    parser.add_argument("--expected-trials", type=int, required=True)
    parser.add_argument("--reward-floor", type=float, default=1.0)
    args = parser.parse_args(argv)

    if args.expected_trials < 1:
        parser.error("--expected-trials must be at least 1")

    try:
        result = load_result(args.result)
    except ValueError as exc:
        print(f"Harbor job check failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_result(result, args.expected_trials, args.reward_floor)
    if errors:
        print("Harbor job check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Harbor job passed: {args.expected_trials} trials, "
        f"reward floor {args.reward_floor:g}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
