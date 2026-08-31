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
        self.assertEqual(job.total_tokens, 1100)
        self.assertEqual(job.verified_successes(0.9), 3)
        self.assertAlmostEqual(job.tokens_per_verified_success(0.9), 1100 / 3)
        self.assertAlmostEqual(job.cost_per_verified_success(0.9), 0.3)
        self.assertTrue(job.reliable)
        self.assertTrue(job.token_usage_available)
        self.assertEqual(job.token_usage_source, "harbor-result")

    def test_recovers_tokens_from_raw_codex_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = result_data(1.0, trials=1)
            stats = data["stats"]
            assert isinstance(stats, dict)
            stats["n_input_tokens"] = None
            stats["n_cache_tokens"] = None
            stats["n_output_tokens"] = None
            stats["cost_usd"] = None
            path = self.write_job(root, "candidate", data)
            log = root / "candidate" / "trial-1" / "agent" / "codex.txt"
            log.parent.mkdir(parents=True)
            log.write_bytes(
                b"non-json setup output\n"
                + json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 1200,
                            "cached_input_tokens": 900,
                            "output_tokens": 80,
                        },
                    }
                ).encode("utf-8")
                + b"\ninvalid utf-8: \x9d\n"
            )
            job = summary.load_job(path, "Candidate")

        self.assertEqual(job.uncached_input_tokens, 300)
        self.assertEqual(job.cached_input_tokens, 900)
        self.assertEqual(job.output_tokens, 80)
        self.assertEqual(job.total_tokens, 1280)
        self.assertTrue(job.token_usage_available)
        self.assertEqual(job.token_usage_source, "codex-event-fallback")
        self.assertIsNone(job.cost_usd)

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
        self.assertIn("Verified-success efficiency", report)
        self.assertIn("Tokens / verified success", report)
        self.assertIn("http://127.0.0.1:8080/jobs/candidate", report)

    def test_efficiency_requires_verified_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = summary.load_job(
                self.write_job(root, "previous", result_data(0.8)), "Previous"
            )
            candidate = summary.load_job(
                self.write_job(root, "candidate", result_data(1.0)), "Candidate"
            )

        self.assertIn(
            "previous did not",
            summary.assess_efficiency(previous, candidate, 1.0),
        )

    def test_efficiency_leads_with_tokens_when_cost_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = summary.load_job(
                self.write_job(root, "previous", result_data(0.8)), "Previous"
            )
            candidate = summary.load_job(
                self.write_job(root, "candidate", result_data(1.0)), "Candidate"
            )

        assessment = summary.assess_efficiency(previous, candidate, 0.8)
        self.assertTrue(
            assessment.startswith("candidate tokens per verified success")
        )
        self.assertIn("candidate cost per verified success", assessment)

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

    def test_builds_machine_readable_evaluation_cell(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jobs = [
                summary.load_job(
                    self.write_job(root, name, result_data(reward)), label
                )
                for name, label, reward in (
                    ("no-skill", "No skill", 0.7),
                    ("previous", "Previous", 0.8),
                    ("candidate", "Candidate", 1.0),
                )
            ]
            cell = summary.build_evaluation_cell(
                cell_id="uxl-onetbb-example-calibration",
                stage="calibration",
                skill_name="uxl-onetbb",
                task_name="onetbb-join-node-ordering",
                no_skill=jobs[0],
                previous=jobs[1],
                candidate=jobs[2],
                repository="https://github.com/uxlfoundation/skills.git",
                task_commit="1" * 40,
                task_content_sha256="a" * 64,
                task_dirty=False,
                verifier_sha256="b" * 64,
                previous_commit="2" * 40,
                previous_content_sha256="c" * 64,
                candidate_commit="3" * 40,
                candidate_content_sha256="d" * 64,
                candidate_dirty=False,
                agent="codex",
                harness_version="0.20.0",
                model="example-model",
                reasoning_effort="medium",
                environment="hosted-container",
                os_name="ubuntu-24.04",
                architecture="x86_64",
                container_image=None,
                container_digest=None,
                toolchain={"python": "3.12.8", "harbor": "0.20.0"},
                hardware_class="generic-cpu",
                hardware_probe_sha256=None,
                attempts=3,
                timeout_seconds=900,
                concurrency=1,
                verified_reward_floor=1.0,
                max_age_days=90,
            )

        self.assertEqual(cell["schema_version"], "1.0")
        self.assertEqual(cell["results"]["arms"]["candidate-skill"]["verified_successes"], 3)


if __name__ == "__main__":
    unittest.main()
