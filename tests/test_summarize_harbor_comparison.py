from __future__ import annotations

import json
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_harbor_comparison as summary  # noqa: E402


def result_data(
    reward: float,
    *,
    trials: int = 3,
    completed: int | None = None,
    errors: int = 0,
    use_mean: bool = False,
) -> dict[str, object]:
    completed = trials if completed is None else completed
    metric = {"mean": reward} if use_mean else {
        "answer_present": 1.0,
        "required_terms": reward,
        "reward": reward,
    }
    trial_ids = [f"trial-{index}" for index in range(completed)]
    return {
        "started_at": "2026-08-07T10:00:00",
        "finished_at": "2026-08-07T10:02:00",
        "n_total_trials": trials,
        "stats": {
            "n_completed_trials": completed,
            "n_errored_trials": errors,
            "n_running_trials": 0,
            "n_pending_trials": max(trials - completed - errors, 0),
            "n_cancelled_trials": 0,
            "evals": {
                "codex__model__tasks": {
                    "n_trials": completed,
                    "n_errors": errors,
                    "metrics": [metric],
                    "reward_stats": {"reward": {str(reward): trial_ids}},
                }
            },
            "n_input_tokens": 1000,
            "n_cache_tokens": 700,
            "n_output_tokens": 100,
            "cost_usd": reward,
        },
    }


class HarborComparisonTests(unittest.TestCase):
    def write_job(self, root: Path, name: str, data: dict[str, object]) -> Path:
        path = root / name / "result.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_loads_component_metrics_and_uncached_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_job(Path(directory), "candidate", result_data(0.9))
            job = summary.load_job(path, "Candidate")

        self.assertEqual(job.mean_reward, 0.9)
        self.assertEqual(job.metrics["required_terms"], 0.9)
        self.assertEqual(job.uncached_input_tokens, 300)
        self.assertEqual(job.cached_input_tokens, 700)
        self.assertEqual(job.trial_rewards, (0.9, 0.9, 0.9))
        self.assertTrue(job.reliable)

    def test_mean_metric_is_normalized_to_reward_and_ceiling_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jobs = [
                summary.load_job(
                    self.write_job(root, name, result_data(1.0, use_mean=True)), label
                )
                for name, label in (
                    ("no-skill", "No skill"),
                    ("previous", "Previous"),
                    ("candidate", "Candidate"),
                )
            ]
            report, failed = summary.render_report(
                skill_name="uxl-onetbb",
                task_name="histogram",
                no_skill=jobs[0],
                previous=jobs[1],
                candidate=jobs[2],
                previous_ref="old",
                candidate_ref="new",
                task_ref="task",
                agent="codex",
                model="model",
                attempts=3,
                dashboard_base_url="http://127.0.0.1:8080",
                tolerance=1e-6,
            )

        self.assertFalse(failed)
        self.assertIn("NO QUALITY CHANGE", report)
        self.assertIn("Ceiling warning", report)
        self.assertIn("http://127.0.0.1:8080/jobs/candidate", report)

    def test_regression_and_incomplete_candidate_fail_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = summary.load_job(
                self.write_job(root, "previous", result_data(0.9)), "Previous"
            )
            regressed = summary.load_job(
                self.write_job(root, "regressed", result_data(0.8)), "Candidate"
            )
            incomplete = summary.load_job(
                self.write_job(
                    root,
                    "incomplete",
                    result_data(1.0, completed=2, errors=1),
                ),
                "Candidate",
            )

        assessment, failed = summary.assess_candidate(previous, regressed, 1e-6)
        self.assertTrue(failed)
        self.assertIn("REGRESSION", assessment)
        assessment, failed = summary.assess_candidate(previous, incomplete, 1e-6)
        self.assertTrue(failed)
        self.assertIn("INVALID", assessment)

    def test_cli_writes_report_and_optionally_fails_on_regression(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            no_skill = self.write_job(root, "no-skill", result_data(0.7))
            previous = self.write_job(root, "previous", result_data(0.9))
            candidate = self.write_job(root, "candidate", result_data(0.8))
            output = root / "comparison.md"
            arguments = [
                "--no-skill",
                str(no_skill),
                "--previous",
                str(previous),
                "--candidate",
                str(candidate),
                "--skill-name",
                "uxl-onemath",
                "--task-name",
                "runtime",
                "--output",
                str(output),
                "--fail-on-regression",
            ]
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exit_code = summary.main(arguments)

            self.assertEqual(exit_code, 2)
            self.assertIn("REGRESSION", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
