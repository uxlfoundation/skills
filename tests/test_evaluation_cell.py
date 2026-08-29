from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_evaluation_cell as cells  # noqa: E402


def revision(commit: str, digest: str) -> dict[str, str]:
    return {
        "repository": "https://github.com/uxlfoundation/skills.git",
        "commit": commit,
        "content_sha256": digest,
    }


def valid_record() -> dict[str, object]:
    arm = {
        "result_path": "harbor-jobs/example/result.json",
        "accepted_attempts": 3,
        "completed_attempts": 3,
        "errored_attempts": 0,
        "excluded_infrastructure_failures": 0,
        "mean_reward": 1.0,
        "verified_successes": 3,
    }
    return {
        "schema_version": "1.0",
        "cell_id": "onetbb-example-codex-calibration",
        "stage": "calibration",
        "recorded_at": "2026-08-28T20:00:00Z",
        "scope": {
            "skill": "uxl-onetbb",
            "task": "onetbb-join-node-ordering",
            "task_revision": revision("1" * 40, "a" * 64),
            "task_dirty": False,
            "verifier_sha256": "b" * 64,
        },
        "treatment": {
            "comparison_arms": list(cells.ARMS),
            "previous_skill": revision("2" * 40, "c" * 64),
            "candidate_skill": revision("3" * 40, "d" * 64),
            "candidate_dirty": False,
        },
        "agent": {
            "name": "codex",
            "harness": "harbor",
            "harness_version": "0.20.0",
            "model": "example-model",
            "reasoning_effort": "medium",
        },
        "execution": {
            "environment": "hosted-container",
            "os": "ubuntu-24.04",
            "architecture": "x86_64",
            "container_image": "example.invalid/uxl/evaluator",
            "container_digest": f"sha256:{'e' * 64}",
            "toolchain": {"python": "3.12.8", "harbor": "0.20.0"},
            "hardware": {"class": "generic-cpu", "probe_sha256": None},
            "attempts_per_arm": 3,
            "timeout_seconds": 900,
            "concurrency": 1,
        },
        "results": {
            "reward_floor": 1.0,
            "arms": {name: copy.deepcopy(arm) for name in cells.ARMS},
        },
        "freshness": {
            "max_age_days": 90,
            "material_dimensions": sorted(cells.MATERIAL_DIMENSIONS),
        },
    }


class EvaluationCellTests(unittest.TestCase):
    def test_valid_matched_calibration_cell(self) -> None:
        self.assertEqual(cells.validate_record(valid_record()), [])

    def test_rejects_mismatched_arms_and_incomplete_attempts(self) -> None:
        record = valid_record()
        treatment = record["treatment"]
        assert isinstance(treatment, dict)
        treatment["comparison_arms"] = ["no-skill", "candidate-skill"]
        results = record["results"]
        assert isinstance(results, dict)
        arms = results["arms"]
        assert isinstance(arms, dict)
        arms["candidate-skill"]["completed_attempts"] = 2

        errors = cells.validate_record(record)

        self.assertTrue(any("comparison_arms" in error for error in errors))
        self.assertTrue(any("completed_attempts" in error for error in errors))

    def test_promotion_requires_five_attempts_and_clean_inputs(self) -> None:
        record = valid_record()
        record["stage"] = "promotion"
        treatment = record["treatment"]
        assert isinstance(treatment, dict)
        treatment["candidate_dirty"] = True
        scope = record["scope"]
        assert isinstance(scope, dict)
        scope["task_dirty"] = True

        errors = cells.validate_record(record)

        self.assertTrue(any("at least 5 attempts" in error for error in errors))
        self.assertTrue(any("candidate_dirty=false" in error for error in errors))
        self.assertTrue(any("task_dirty=false" in error for error in errors))

    def test_specialized_hardware_requires_probe_digest(self) -> None:
        record = valid_record()
        execution = record["execution"]
        assert isinstance(execution, dict)
        execution["environment"] = "target-gpu"
        execution["hardware"] = {"class": "target-gpu", "probe_sha256": None}

        errors = cells.validate_record(record)

        self.assertTrue(any("requires a probe_sha256" in error for error in errors))

    def test_reports_age_and_material_dimension_changes(self) -> None:
        record = valid_record()
        context = copy.deepcopy(record)
        agent = context["agent"]
        assert isinstance(agent, dict)
        agent["model"] = "new-model"

        reasons = cells.staleness_reasons(
            record,
            context,
            datetime(2027, 1, 1, tzinfo=timezone.utc),
        )

        self.assertTrue(any("age exceeds" in reason for reason in reasons))
        self.assertTrue(any("agent.model" in reason for reason in reasons))

    def test_cli_validates_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cell.json"
            path.write_text(json.dumps(valid_record()), encoding="utf-8")
            self.assertEqual(cells.main([str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
