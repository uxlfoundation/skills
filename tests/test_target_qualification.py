from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_target_qualification as qualification  # noqa: E402
import validate_target_qualifications as ledger  # noqa: E402


def valid_record() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "qualification_id": "example-linux-target-gpu-111111111111",
        "recorded_at": "2026-08-29T12:00:00Z",
        "status": "passed",
        "scope": {
            "skill": "uxl-sycl-build-debug",
            "task": "sycl-device-discovery",
            "task_revision": {
                "repository": "https://github.com/uxlfoundation/skills.git",
                "commit": "1" * 40,
                "content_sha256": "2" * 64,
            },
            "verifier_sha256": "3" * 64,
        },
        "lane": {
            "lane_id": "example-linux-target-gpu",
            "adapter_id": "example-target-gpu",
            "display_name": "Example Linux GPU",
            "environment": "manual-gpu",
            "hardware_class": "target-gpu",
            "vendor": "Example Vendor",
            "device": "Example Accelerator",
            "interface": "/dev/example",
            "os": "Example Linux",
            "architecture": "x86_64",
            "control": "access-controlled",
        },
        "evidence": {
            "agent": "oracle",
            "attempts": 1,
            "completed_attempts": 1,
            "errored_attempts": 0,
            "reward": 1.0,
            "result_sha256": "4" * 64,
            "provenance_sha256": "5" * 64,
            "workflow": {"visibility": "access-controlled", "run_id": "12345"},
        },
        "freshness": {"max_age_days": 90},
        "limitations": ["Qualification only; no skill-benefit claim."],
    }


class TargetQualificationTests(unittest.TestCase):
    def test_accepts_sanitized_passing_record(self) -> None:
        self.assertEqual(qualification.validate_record(valid_record()), [])

    def test_rejects_raw_runner_fields_and_nonpassing_evidence(self) -> None:
        record = valid_record()
        lane = record["lane"]
        evidence = record["evidence"]
        assert isinstance(lane, dict) and isinstance(evidence, dict)
        lane["runner_name"] = "private-host"
        evidence["reward"] = 0.5

        errors = qualification.validate_record(record)

        self.assertTrue(any("runner_name is not allowed" in error for error in errors))
        self.assertTrue(any("reward must be 1.0" in error for error in errors))

    def test_ledger_matches_declared_task_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = root / "qualifications"
            records.mkdir()
            record = valid_record()
            record_id = record["qualification_id"]
            (records / f"{record_id}.json").write_text(json.dumps(record), encoding="utf-8")
            suites = root / "suites.json"
            suites.write_text(
                json.dumps(
                    {
                        "suites": [
                            {
                                "skill": "uxl-sycl-build-debug",
                                "tasks": [
                                    {
                                        "name": "sycl-device-discovery",
                                        "status": "implemented",
                                        "environment": "manual-gpu",
                                        "hardware": "target-gpu",
                                    }
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            count, errors = ledger.validate_ledger(records, suites)
            self.assertEqual((count, errors), (1, []))

            changed = copy.deepcopy(record)
            changed_lane = changed["lane"]
            assert isinstance(changed_lane, dict)
            changed_lane["hardware_class"] = "target-device"
            (records / f"{record_id}.json").write_text(json.dumps(changed), encoding="utf-8")
            _, errors = ledger.validate_ledger(records, suites)

        self.assertTrue(any("hardware_class must match" in error for error in errors))

    def test_repository_ledger_is_valid(self) -> None:
        count, errors = ledger.validate_ledger(
            ROOT / "evaluation" / "harbor" / "results" / "qualifications",
            ROOT / "evaluation" / "harbor" / "suites.json",
        )
        self.assertGreaterEqual(count, 1)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
