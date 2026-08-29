#!/usr/bin/env python3
"""Create a human-readable comparison from three native Harbor result files."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import validate_evaluation_cell as evaluation_cells


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
    token_usage_available: bool
    token_usage_source: str
    cost_usd: float | None
    runtime_seconds: float | None

    @property
    def reliable(self) -> bool:
        return (
            self.total_trials > 0
            and self.completed_trials == self.total_trials
            and self.errored_trials == 0
            and self.unfinished_trials == 0
        )

    @property
    def total_tokens(self) -> int:
        return self.uncached_input_tokens + self.cached_input_tokens + self.output_tokens

    def verified_successes(self, reward_floor: float) -> int:
        return sum(reward >= reward_floor for reward in self.trial_rewards)

    def tokens_per_verified_success(self, reward_floor: float) -> float | None:
        if not self.token_usage_available:
            return None
        successes = self.verified_successes(reward_floor)
        return self.total_tokens / successes if successes else None

    def cost_per_verified_success(self, reward_floor: float) -> float | None:
        successes = self.verified_successes(reward_floor)
        return self.cost_usd / successes if successes and self.cost_usd is not None else None


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


def _codex_event_usage(job_directory: Path) -> tuple[int, int, int] | None:
    """Recover usage when Harbor cannot convert the Codex event trajectory."""
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    found = False
    for path in sorted(job_directory.glob("*/agent/codex.txt")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict) or event.get("type") != "turn.completed":
                continue
            usage = event.get("usage")
            if not isinstance(usage, dict):
                continue
            values = {
                name: usage.get(name)
                for name in totals
            }
            if not all(isinstance(value, int) and not isinstance(value, bool) for value in values.values()):
                continue
            found = True
            for name, value in values.items():
                totals[name] += value
    if not found:
        return None
    return (
        totals["input_tokens"],
        totals["cached_input_tokens"],
        totals["output_tokens"],
    )


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

    harbor_token_values = (
        stats.get("n_input_tokens"),
        stats.get("n_cache_tokens"),
        stats.get("n_output_tokens"),
    )
    token_usage_available = all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in harbor_token_values
    )
    token_usage_source = "harbor-result" if token_usage_available else "unavailable"
    if token_usage_available:
        total_input, cached_input, output_tokens = (
            int(value) for value in harbor_token_values
        )
    else:
        recovered_usage = _codex_event_usage(path.parent)
        if recovered_usage is None:
            total_input = cached_input = output_tokens = 0
        else:
            total_input, cached_input, output_tokens = recovered_usage
            token_usage_available = True
            token_usage_source = "codex-event-fallback"
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
        output_tokens=output_tokens,
        token_usage_available=token_usage_available,
        token_usage_source=token_usage_source,
        cost_usd=_number(stats.get("cost_usd")),
        runtime_seconds=_runtime_seconds(result),
    )


def _format_reward(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _format_delta(candidate: float | None, reference: float | None) -> str:
    if candidate is None or reference is None:
        return "n/a"
    return f"{candidate - reference:+.4f}"


def _format_percent(candidate: float | None, reference: float | None) -> str:
    if candidate is None or reference is None:
        return "n/a"
    if reference == 0:
        return "n/a" if candidate == 0 else "+inf"
    return f"{((candidate / reference) - 1.0) * 100:+.1f}%"


def _format_runtime(value: float | None) -> str:
    if value is None:
        return "n/a"
    minutes, seconds = divmod(round(value), 60)
    return f"{minutes}m {seconds:02d}s" if minutes else f"{seconds}s"


def _format_tokens_per_success(value: float | None) -> str:
    return "n/a" if value is None else f"{round(value):,}"


def _format_cost_per_success(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.6f}"


def _format_cost(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.6f}"


def _format_tokens(value: int, available: bool) -> str:
    return f"{value:,}" if available else "n/a"


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
    previous: JobSummary,
    candidate: JobSummary,
    tolerance: float,
    verified_reward_floor: float = 1.0,
) -> tuple[str, bool]:
    if not candidate.reliable:
        return "INVALID: candidate run is incomplete or errored", True
    if candidate.mean_reward is None:
        return "INVALID: candidate run has no aggregate reward", True
    if previous.mean_reward is None:
        return "UNKNOWN: previous run has no aggregate reward", False
    previous_successes = previous.verified_successes(verified_reward_floor)
    candidate_successes = candidate.verified_successes(verified_reward_floor)
    if candidate_successes < previous_successes:
        return (
            "REGRESSION: candidate verified successes changed from "
            f"{previous_successes} to {candidate_successes}",
            True,
        )
    delta = candidate.mean_reward - previous.mean_reward
    if delta < -tolerance:
        return f"REGRESSION: candidate reward changed by {delta:+.4f}", True
    if delta > tolerance:
        return f"IMPROVEMENT: candidate reward changed by {delta:+.4f}", False
    return f"NO QUALITY CHANGE: reward changed by {delta:+.4f}", False


def assess_efficiency(
    previous: JobSummary, candidate: JobSummary, verified_reward_floor: float
) -> str:
    previous_successes = previous.verified_successes(verified_reward_floor)
    candidate_successes = candidate.verified_successes(verified_reward_floor)
    if candidate_successes == 0:
        return "UNAVAILABLE: candidate produced no verified success"
    if previous_successes == 0:
        return "IMPROVEMENT: candidate produced a verified success and previous did not"
    assessments: list[str] = []
    previous_tokens = previous.tokens_per_verified_success(verified_reward_floor)
    candidate_tokens = candidate.tokens_per_verified_success(verified_reward_floor)
    if previous_tokens is not None and candidate_tokens is not None:
        assessments.append(
            "candidate tokens per verified success changed by "
            f"{_format_percent(candidate_tokens, previous_tokens)}"
        )
    previous_cost = previous.cost_per_verified_success(verified_reward_floor)
    candidate_cost = candidate.cost_per_verified_success(verified_reward_floor)
    if previous_cost is not None and candidate_cost is not None:
        assessments.append(
            f"candidate cost per verified success changed by "
            f"{_format_percent(candidate_cost, previous_cost)}"
        )
    if assessments:
        return "; ".join(assessments)
    return "UNAVAILABLE: cost and comparable token usage were not reported"


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
    verified_reward_floor: float = 1.0,
) -> tuple[str, bool]:
    assessment, failed = assess_candidate(
        previous, candidate, tolerance, verified_reward_floor
    )
    efficiency_assessment = assess_efficiency(
        previous, candidate, verified_reward_floor
    )
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
        f"- Quality gate at reward `{verified_reward_floor:.4f}`: candidate "
        f"{candidate.verified_successes(verified_reward_floor)}/{candidate.completed_trials}, "
        f"previous {previous.verified_successes(verified_reward_floor)}/{previous.completed_trials}.",
        f"- Efficiency: {efficiency_assessment}.",
        f"- Reliability: {'all runs completed without errors' if all_reliable else 'one or more runs are incomplete or errored'}.",
    ]
    fallback_labels = [
        job.label for job in jobs if job.token_usage_source == "codex-event-fallback"
    ]
    if fallback_labels:
        lines.append(
            "- Token accounting: recovered from raw Codex `turn.completed` events for "
            f"{', '.join(fallback_labels)} because Harbor did not populate job-level usage."
        )
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
            f"{_format_tokens(job.uncached_input_tokens, job.token_usage_available)} | "
            f"{_format_tokens(job.cached_input_tokens, job.token_usage_available)} | "
            f"{_format_tokens(job.output_tokens, job.token_usage_available)} | "
            f"{_format_cost(job.cost_usd)} | {_format_runtime(job.runtime_seconds)} |"
        )

    lines.extend(
        [
            "",
            "## Verified-success efficiency",
            "",
            f"Quality gate: trial reward at least `{verified_reward_floor:.4f}`.",
            "",
            "| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for job in jobs:
        lines.append(
            f"| {job.label} | {job.verified_successes(verified_reward_floor)}/{job.completed_trials} | "
            f"{_format_tokens(job.total_tokens, job.token_usage_available)} | "
            f"{_format_tokens_per_success(job.tokens_per_verified_success(verified_reward_floor))} | "
            f"{_format_cost_per_success(job.cost_per_verified_success(verified_reward_floor))} |"
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
            f"- Verified reward floor: `{verified_reward_floor:.4f}`",
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


def build_evaluation_cell(
    *,
    cell_id: str,
    stage: str,
    skill_name: str,
    task_name: str,
    no_skill: JobSummary,
    previous: JobSummary,
    candidate: JobSummary,
    repository: str,
    task_commit: str,
    task_content_sha256: str,
    task_dirty: bool,
    verifier_sha256: str,
    previous_commit: str,
    previous_content_sha256: str,
    candidate_commit: str,
    candidate_content_sha256: str,
    candidate_dirty: bool,
    agent: str,
    harness_version: str,
    model: str,
    reasoning_effort: str,
    environment: str,
    os_name: str,
    architecture: str,
    container_image: str | None,
    container_digest: str | None,
    toolchain: dict[str, str],
    hardware_class: str,
    hardware_probe_sha256: str | None,
    attempts: int,
    timeout_seconds: int,
    concurrency: int,
    verified_reward_floor: float,
    max_age_days: int,
) -> dict[str, Any]:
    jobs = {
        "no-skill": no_skill,
        "previous-skill": previous,
        "candidate-skill": candidate,
    }
    arms: dict[str, dict[str, Any]] = {}
    for name, job in jobs.items():
        if job.mean_reward is None:
            raise ValueError(f"{name} has no aggregate reward")
        arms[name] = {
            "result_path": _display_path(job.path),
            "accepted_attempts": job.total_trials,
            "completed_attempts": job.completed_trials,
            "errored_attempts": job.errored_trials + job.unfinished_trials,
            "excluded_infrastructure_failures": 0,
            "mean_reward": job.mean_reward,
            "verified_successes": job.verified_successes(verified_reward_floor),
        }
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "cell_id": cell_id,
        "stage": stage,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": {
            "skill": skill_name,
            "task": task_name,
            "task_revision": {
                "repository": repository,
                "commit": task_commit,
                "content_sha256": task_content_sha256,
            },
            "task_dirty": task_dirty,
            "verifier_sha256": verifier_sha256,
        },
        "treatment": {
            "comparison_arms": list(evaluation_cells.ARMS),
            "previous_skill": {
                "repository": repository,
                "commit": previous_commit,
                "content_sha256": previous_content_sha256,
            },
            "candidate_skill": {
                "repository": repository,
                "commit": candidate_commit,
                "content_sha256": candidate_content_sha256,
            },
            "candidate_dirty": candidate_dirty,
        },
        "agent": {
            "name": agent,
            "harness": "harbor",
            "harness_version": harness_version,
            "model": model,
            "reasoning_effort": reasoning_effort,
        },
        "execution": {
            "environment": environment,
            "os": os_name,
            "architecture": architecture,
            "container_image": container_image,
            "container_digest": container_digest,
            "toolchain": toolchain,
            "hardware": {
                "class": hardware_class,
                "probe_sha256": hardware_probe_sha256,
            },
            "attempts_per_arm": attempts,
            "timeout_seconds": timeout_seconds,
            "concurrency": concurrency,
        },
        "results": {
            "reward_floor": verified_reward_floor,
            "arms": arms,
        },
        "freshness": {
            "max_age_days": max_age_days,
            "material_dimensions": [
                "scope.task_revision.commit",
                "scope.task_revision.content_sha256",
                "scope.task_dirty",
                "scope.verifier_sha256",
                "treatment.previous_skill.commit",
                "treatment.previous_skill.content_sha256",
                "treatment.candidate_skill.commit",
                "treatment.candidate_skill.content_sha256",
                "agent.name",
                "agent.harness",
                "agent.harness_version",
                "agent.model",
                "agent.reasoning_effort",
                "execution.environment",
                "execution.os",
                "execution.architecture",
                "execution.container_image",
                "execution.container_digest",
                "execution.toolchain",
                "execution.hardware.class",
                "execution.hardware.probe_sha256",
                "execution.attempts_per_arm",
                "execution.timeout_seconds",
                "execution.concurrency",
            ],
        },
    }
    errors = evaluation_cells.validate_record(record)
    if errors:
        raise ValueError("invalid evaluation cell: " + "; ".join(errors))
    return record


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
    parser.add_argument("--verified-reward-floor", type=float, default=1.0)
    parser.add_argument("--fail-on-regression", action="store_true")
    parser.add_argument("--cell-output", type=Path)
    parser.add_argument("--cell-id")
    parser.add_argument(
        "--cell-stage", choices=("development", "calibration", "promotion")
    )
    parser.add_argument("--repository")
    parser.add_argument("--task-commit")
    parser.add_argument("--task-content-sha256")
    parser.add_argument("--task-dirty", action="store_true")
    parser.add_argument("--verifier-sha256")
    parser.add_argument("--previous-commit")
    parser.add_argument("--previous-content-sha256")
    parser.add_argument("--candidate-commit")
    parser.add_argument("--candidate-content-sha256")
    parser.add_argument("--candidate-dirty", action="store_true")
    parser.add_argument("--harness-version")
    parser.add_argument("--reasoning-effort", default="unknown")
    parser.add_argument("--environment")
    parser.add_argument("--os-name")
    parser.add_argument("--architecture")
    parser.add_argument("--container-image")
    parser.add_argument("--container-digest")
    parser.add_argument("--toolchain-json")
    parser.add_argument("--hardware-class")
    parser.add_argument("--hardware-probe-sha256")
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--cell-max-age-days", type=int, default=90)
    args = parser.parse_args(argv)

    if args.reward_tolerance < 0:
        parser.error("--reward-tolerance cannot be negative")
    if not 0 <= args.verified_reward_floor <= 1:
        parser.error("--verified-reward-floor must be between 0 and 1")

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
        verified_reward_floor=args.verified_reward_floor,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote Harbor comparison: {args.output}")
    if args.cell_output:
        required = {
            "cell-id": args.cell_id,
            "cell-stage": args.cell_stage,
            "repository": args.repository,
            "task-commit": args.task_commit,
            "task-content-sha256": args.task_content_sha256,
            "verifier-sha256": args.verifier_sha256,
            "previous-commit": args.previous_commit,
            "previous-content-sha256": args.previous_content_sha256,
            "candidate-commit": args.candidate_commit,
            "candidate-content-sha256": args.candidate_content_sha256,
            "harness-version": args.harness_version,
            "environment": args.environment,
            "os-name": args.os_name,
            "architecture": args.architecture,
            "toolchain-json": args.toolchain_json,
            "hardware-class": args.hardware_class,
            "timeout-seconds": args.timeout_seconds,
        }
        missing = [name for name, value in required.items() if value in (None, "")]
        if missing:
            print(
                "Evaluation cell output requires: " + ", ".join(missing),
                file=sys.stderr,
            )
            return 1
        try:
            raw_toolchain = json.loads(args.toolchain_json)
            if not isinstance(raw_toolchain, dict) or not all(
                isinstance(name, str) and isinstance(value, str)
                for name, value in raw_toolchain.items()
            ):
                raise ValueError("--toolchain-json must be an object of string values")
            cell = build_evaluation_cell(
                cell_id=args.cell_id,
                stage=args.cell_stage,
                skill_name=args.skill_name,
                task_name=args.task_name,
                no_skill=no_skill,
                previous=previous,
                candidate=candidate,
                repository=args.repository,
                task_commit=args.task_commit,
                task_content_sha256=args.task_content_sha256,
                task_dirty=args.task_dirty,
                verifier_sha256=args.verifier_sha256,
                previous_commit=args.previous_commit,
                previous_content_sha256=args.previous_content_sha256,
                candidate_commit=args.candidate_commit,
                candidate_content_sha256=args.candidate_content_sha256,
                candidate_dirty=args.candidate_dirty,
                agent=args.agent,
                harness_version=args.harness_version,
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                environment=args.environment,
                os_name=args.os_name,
                architecture=args.architecture,
                container_image=args.container_image,
                container_digest=args.container_digest,
                toolchain=raw_toolchain,
                hardware_class=args.hardware_class,
                hardware_probe_sha256=args.hardware_probe_sha256,
                attempts=args.attempts,
                timeout_seconds=args.timeout_seconds,
                concurrency=args.concurrency,
                verified_reward_floor=args.verified_reward_floor,
                max_age_days=args.cell_max_age_days,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"Evaluation cell generation failed: {exc}", file=sys.stderr)
            return 1
        args.cell_output.parent.mkdir(parents=True, exist_ok=True)
        args.cell_output.write_text(
            json.dumps(cell, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"Wrote evaluation cell: {args.cell_output}")
    if failed and args.fail_on_regression:
        print("Candidate comparison failed the regression policy.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
