#!/usr/bin/env python3
"""Create a human-readable comparison from three native Harbor result files."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


@dataclass(frozen=True)
class JobSummary:
    label: str
    path: Path
    job_name: str
    total_trials: int
    completed_trials: int
    errored_trials: int
    unfinished_trials: int
    mean_reward: float | None
    metrics: dict[str, float]
    trial_rewards: tuple[float, ...]
    uncached_input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cost_usd: float
    runtime_seconds: float | None

    @property
    def reliable(self) -> bool:
        return (
            self.total_trials > 0
            and self.completed_trials == self.total_trials
            and self.errored_trials == 0
            and self.unfinished_trials == 0
        )


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _integer(value: Any) -> int:
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else 0


def _metrics_for_eval(eval_stats: dict[str, Any]) -> dict[str, float]:
    raw_metrics = eval_stats.get("metrics")
    if isinstance(raw_metrics, dict):
        records = [raw_metrics]
    elif isinstance(raw_metrics, list):
        records = [item for item in raw_metrics if isinstance(item, dict)]
    else:
        records = []

    values: dict[str, list[float]] = {}
    for record in records:
        for name, raw_value in record.items():
            value = _number(raw_value)
            if value is not None:
                values.setdefault(str(name), []).append(value)

    metrics = {name: sum(items) / len(items) for name, items in values.items()}
    if "reward" not in metrics and "mean" in metrics:
        metrics["reward"] = metrics.pop("mean")
    return metrics


def _aggregate_metrics(evals: dict[str, Any]) -> dict[str, float]:
    weighted_values: dict[str, float] = {}
    weights: dict[str, float] = {}
    for raw_eval in evals.values():
        if not isinstance(raw_eval, dict):
            continue
        metrics = _metrics_for_eval(raw_eval)
        weight = max(_integer(raw_eval.get("n_trials")), 1)
        for name, value in metrics.items():
            weighted_values[name] = weighted_values.get(name, 0.0) + value * weight
            weights[name] = weights.get(name, 0.0) + weight
    return {
        name: weighted_values[name] / weights[name]
        for name in sorted(weighted_values)
    }


def _trial_rewards(evals: dict[str, Any]) -> tuple[float, ...]:
    rewards: list[float] = []
    for raw_eval in evals.values():
        if not isinstance(raw_eval, dict):
            continue
        reward_stats = raw_eval.get("reward_stats")
        if not isinstance(reward_stats, dict):
            continue
        reward_buckets = reward_stats.get("reward")
        if not isinstance(reward_buckets, dict):
            continue
        for raw_reward, trial_ids in reward_buckets.items():
            try:
                reward = float(raw_reward)
            except (TypeError, ValueError):
                continue
            count = len(trial_ids) if isinstance(trial_ids, list) else 0
            rewards.extend([reward] * count)
    return tuple(sorted(rewards))


def _runtime_seconds(result: dict[str, Any]) -> float | None:
    started = result.get("started_at")
    finished = result.get("finished_at")
    if not isinstance(started, str) or not isinstance(finished, str):
        return None
    try:
        return max(
            (datetime.fromisoformat(finished) - datetime.fromisoformat(started)).total_seconds(),
            0.0,
        )
    except ValueError:
        return None


def load_job(path: Path, label: str) -> JobSummary:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} result does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} result is not valid JSON: {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"{label} result must be a JSON object: {path}")

    stats = result.get("stats")
    if not isinstance(stats, dict):
        raise ValueError(f"{label} result.stats is missing or invalid: {path}")
    evals = stats.get("evals")
    if not isinstance(evals, dict):
        evals = {}

    total_input = _integer(stats.get("n_input_tokens"))
    cached_input = _integer(stats.get("n_cache_tokens"))
    unfinished = sum(
        _integer(stats.get(name))
        for name in ("n_running_trials", "n_pending_trials", "n_cancelled_trials")
    )
    metrics = _aggregate_metrics(evals)
    return JobSummary(
        label=label,
        path=path,
        job_name=path.parent.name,
        total_trials=_integer(result.get("n_total_trials")),
        completed_trials=_integer(stats.get("n_completed_trials")),
        errored_trials=_integer(stats.get("n_errored_trials")),
        unfinished_trials=unfinished,
        mean_reward=metrics.get("reward"),
        metrics=metrics,
        trial_rewards=_trial_rewards(evals),
        uncached_input_tokens=max(total_input - cached_input, 0),
        cached_input_tokens=cached_input,
        output_tokens=_integer(stats.get("n_output_tokens")),
        cost_usd=_number(stats.get("cost_usd")) or 0.0,
        runtime_seconds=_runtime_seconds(result),
    )


def _format_reward(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _format_delta(candidate: float | None, reference: float | None) -> str:
    if candidate is None or reference is None:
        return "n/a"
    return f"{candidate - reference:+.4f}"


def _format_percent(candidate: float, reference: float) -> str:
    if reference == 0:
        return "n/a" if candidate == 0 else "+inf"
    return f"{((candidate / reference) - 1.0) * 100:+.1f}%"


def _format_runtime(value: float | None) -> str:
    if value is None:
        return "n/a"
    minutes, seconds = divmod(round(value), 60)
    return f"{minutes}m {seconds:02d}s" if minutes else f"{seconds}s"


def _format_trial_rewards(values: tuple[float, ...]) -> str:
    if not values:
        return "n/a"
    buckets: list[str] = []
    for value in sorted(set(values)):
        count = values.count(value)
        buckets.append(f"{value:.4f}x{count}")
    return ", ".join(buckets)


def _job_link(job: JobSummary, dashboard_base_url: str | None) -> str:
    label = f"`{job.job_name}`"
    if not dashboard_base_url:
        return label
    url = f"{dashboard_base_url.rstrip('/')}/jobs/{quote(job.job_name)}"
    return f"[{label}]({url})"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(path)


def assess_candidate(
    previous: JobSummary, candidate: JobSummary, tolerance: float
) -> tuple[str, bool]:
    if not candidate.reliable:
        return "INVALID: candidate run is incomplete or errored", True
    if candidate.mean_reward is None:
        return "INVALID: candidate run has no aggregate reward", True
    if previous.mean_reward is None:
        return "UNKNOWN: previous run has no aggregate reward", False
    delta = candidate.mean_reward - previous.mean_reward
    if delta < -tolerance:
        return f"REGRESSION: candidate reward changed by {delta:+.4f}", True
    if delta > tolerance:
        return f"IMPROVEMENT: candidate reward changed by {delta:+.4f}", False
    return f"NO QUALITY CHANGE: reward changed by {delta:+.4f}", False


def render_report(
    *,
    skill_name: str,
    task_name: str,
    no_skill: JobSummary,
    previous: JobSummary,
    candidate: JobSummary,
    previous_ref: str,
    candidate_ref: str,
    task_ref: str,
    agent: str,
    model: str,
    attempts: int,
    dashboard_base_url: str | None,
    tolerance: float,
) -> tuple[str, bool]:
    assessment, failed = assess_candidate(previous, candidate, tolerance)
    jobs = (no_skill, previous, candidate)
    all_reliable = all(job.reliable for job in jobs)
    ceiling = all(
        job.mean_reward is not None and job.mean_reward >= 1.0 - tolerance
        for job in jobs
    )

    lines = [
        f"# Harbor skill comparison: `{skill_name}`",
        "",
        f"Task: `{task_name}`",
        "",
        "## Outcome",
        "",
        f"- **{assessment}**",
        f"- Candidate versus no skill: {_format_delta(candidate.mean_reward, no_skill.mean_reward)} reward.",
        f"- Candidate versus previous: {_format_delta(candidate.mean_reward, previous.mean_reward)} reward, "
        f"{_format_percent(candidate.cost_usd, previous.cost_usd)} cost.",
        f"- Reliability: {'all runs completed without errors' if all_reliable else 'one or more runs are incomplete or errored'}.",
    ]
    if ceiling:
        lines.append(
            "- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value."
        )

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |",
            "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for job in jobs:
        lines.append(
            f"| {job.label} | {_job_link(job, dashboard_base_url)} | "
            f"{_format_reward(job.mean_reward)} | {job.completed_trials}/{job.total_trials} | "
            f"{job.errored_trials} | {_format_trial_rewards(job.trial_rewards)} | "
            f"{job.uncached_input_tokens:,} | {job.cached_input_tokens:,} | "
            f"{job.output_tokens:,} | ${job.cost_usd:.6f} | {_format_runtime(job.runtime_seconds)} |"
        )

    metric_names = sorted(
        set(no_skill.metrics) | set(previous.metrics) | set(candidate.metrics)
    )
    if metric_names:
        lines.extend(
            [
                "",
                "## Metric breakdown",
                "",
                "| Metric | No skill | Previous | Candidate | Candidate - previous |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for name in metric_names:
            previous_value = previous.metrics.get(name)
            candidate_value = candidate.metrics.get(name)
            lines.append(
                f"| `{name}` | {_format_reward(no_skill.metrics.get(name))} | "
                f"{_format_reward(previous_value)} | {_format_reward(candidate_value)} | "
                f"{_format_delta(candidate_value, previous_value)} |"
            )

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"- Task: `{task_ref}`",
            f"- Previous skill: `{previous_ref}`",
            f"- Candidate skill: `{candidate_ref}`",
            f"- Agent/model: `{agent}` / `{model}`",
            f"- Attempts per arm: `{attempts}`",
            f"- No-skill result: `{_display_path(no_skill.path)}`",
            f"- Previous result: `{_display_path(previous.path)}`",
            f"- Candidate result: `{_display_path(candidate.path)}`",
            "",
            "Review any changed or failed trial in Harbor: inspect **Verifier** for the score, "
            "**Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.",
            "",
        ]
    )
    return "\n".join(lines), failed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-skill", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--task-name", required=True)
    parser.add_argument("--previous-ref", default="unknown")
    parser.add_argument("--candidate-ref", default="working tree")
    parser.add_argument("--task-ref", default="unknown")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--model", default="unknown")
    parser.add_argument("--attempts", type=int, default=0)
    parser.add_argument("--dashboard-base-url")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reward-tolerance", type=float, default=1e-6)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args(argv)

    if args.reward_tolerance < 0:
        parser.error("--reward-tolerance cannot be negative")

    try:
        no_skill = load_job(args.no_skill, "No skill")
        previous = load_job(args.previous, "Previous")
        candidate = load_job(args.candidate, "Candidate")
    except ValueError as exc:
        print(f"Harbor comparison failed: {exc}", file=sys.stderr)
        return 1

    report, failed = render_report(
        skill_name=args.skill_name,
        task_name=args.task_name,
        no_skill=no_skill,
        previous=previous,
        candidate=candidate,
        previous_ref=args.previous_ref,
        candidate_ref=args.candidate_ref,
        task_ref=args.task_ref,
        agent=args.agent,
        model=args.model,
        attempts=args.attempts,
        dashboard_base_url=args.dashboard_base_url,
        tolerance=args.reward_tolerance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote Harbor comparison: {args.output}")
    if failed and args.fail_on_regression:
        print("Candidate comparison failed the regression policy.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
