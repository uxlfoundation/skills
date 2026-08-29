from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import import_harbor_artifact  # noqa: E402


def job_result(reward: float = 1.0) -> dict:
    return {
        "n_total_trials": 1,
        "finished_at": "2026-08-18T12:00:00Z",
        "stats": {
            "n_completed_trials": 1,
            "evals": {"oracle": {"metrics": [{"reward": reward}]}},
        },
    }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def qualification_record(result_bytes: bytes, provenance_bytes: bytes) -> dict:
    return {
        "schema_version": "1.0",
        "qualification_id": "lab-gpu-20260829-aaaaaaaaaaaa",
        "recorded_at": "2026-08-29T12:00:00Z",
        "status": "passed",
        "scope": {
            "skill": "sample-skill",
            "task": "sample-task",
            "task_revision": {
                "repository": "https://github.com/uxlfoundation/skills",
                "commit": "a" * 40,
                "content_sha256": "b" * 64,
            },
            "verifier_sha256": "c" * 64,
        },
        "lane": {
            "lane_id": "lab-gpu",
            "adapter_id": "lab-gpu",
            "display_name": "Laboratory GPU",
            "environment": "target-gpu",
            "hardware_class": "target-gpu",
            "vendor": "Example Vendor",
            "device": "Example GPU",
            "interface": "Native runtime",
            "os": "Linux",
            "architecture": "x86_64",
            "control": "access-controlled",
        },
        "evidence": {
            "agent": "oracle",
            "attempts": 1,
            "completed_attempts": 1,
            "errored_attempts": 0,
            "reward": 1.0,
            "result_sha256": sha256_bytes(result_bytes),
            "provenance_sha256": sha256_bytes(provenance_bytes),
            "workflow": {"visibility": "access-controlled", "run_id": "1234"},
        },
        "freshness": {"max_age_days": 90},
        "limitations": ["Qualification covers one task and one device configuration."],
    }


class ImportHarborArtifactTests(unittest.TestCase):
    def test_imports_job_and_shared_provenance_from_zip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "gpu-evidence.zip"
            jobs = root / "jobs"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("runner-provenance.json", '{"qualified": true}\n')
                bundle.writestr("uxl-gpu-oracle/result.json", json.dumps(job_result()))
                bundle.writestr("uxl-gpu-oracle/trial/verifier.log", "passed\n")

            imported = import_harbor_artifact.run(archive, jobs, replace=False)

            self.assertEqual(imported[0][0], "imported")
            destination = jobs / "uxl-gpu-oracle"
            self.assertTrue((destination / "result.json").is_file())
            self.assertTrue((destination / "runner-provenance.json").is_file())
            manifest = json.loads(
                (destination / "import-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["source_artifact"], archive.name)
            self.assertTrue(manifest["runner_provenance_included"])

            repeated = import_harbor_artifact.run(archive, jobs, replace=False)
            self.assertEqual(repeated[0][0], "unchanged")

    def test_stages_evidence_bound_qualification_for_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "qualified-target.zip"
            jobs = root / "jobs"
            result_bytes = (json.dumps(job_result()) + "\n").encode()
            provenance = {
                "adapter_id": "lab-gpu",
                "source_commit": "a" * 40,
                "task": {
                    "skill": "sample-skill",
                    "name": "sample-task",
                    "hardware_class": "target-gpu",
                },
                "oracle": {
                    "status": "passed",
                    "result_path": "harbor-jobs/lab-oracle/result.json",
                },
            }
            provenance_bytes = (json.dumps(provenance) + "\n").encode()
            record = qualification_record(result_bytes, provenance_bytes)
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("runner-provenance.json", provenance_bytes)
                bundle.writestr("harbor-jobs/lab-oracle/result.json", result_bytes)
                bundle.writestr("qualification-record.json", json.dumps(record))

            outcome = import_harbor_artifact.run_with_review(archive, jobs, replace=False)

            self.assertEqual(outcome.jobs[0][0], "imported")
            self.assertEqual(outcome.qualification_candidates[0][0], "staged")
            candidate = jobs / "qualification-review" / f"{record['qualification_id']}.json"
            self.assertEqual(json.loads(candidate.read_text(encoding="utf-8")), record)

    def test_rejects_qualification_not_bound_to_artifact_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "mismatched-target.zip"
            result_bytes = (json.dumps(job_result()) + "\n").encode()
            provenance_bytes = b'{"qualified": true}\n'
            record = qualification_record(result_bytes, provenance_bytes)
            record["evidence"]["result_sha256"] = "f" * 64
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("runner-provenance.json", provenance_bytes)
                bundle.writestr("harbor-jobs/lab-oracle/result.json", result_bytes)
                bundle.writestr("qualification-record.json", json.dumps(record))

            with self.assertRaisesRegex(ValueError, "does not match a Harbor result"):
                import_harbor_artifact.run_with_review(archive, root / "jobs", replace=False)
            self.assertFalse((root / "jobs").exists())

    def test_rejects_malformed_qualification_before_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "malformed-target.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("lab-oracle/result.json", json.dumps(job_result()))
                bundle.writestr("qualification-record.json", '{"schema_version": "1.0"}')

            with self.assertRaisesRegex(ValueError, "failed validation"):
                import_harbor_artifact.run_with_review(archive, root / "jobs", replace=False)
            self.assertFalse((root / "jobs").exists())

    def test_rejects_archive_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "malicious.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("../outside.txt", "unsafe")
            with self.assertRaisesRegex(ValueError, "unsafe archive path"):
                import_harbor_artifact.run(archive, root / "jobs", replace=False)
            self.assertFalse((root / "outside.txt").exists())

    def test_refuses_to_overwrite_a_different_job_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact"
            source_job = artifact / "same-name"
            source_job.mkdir(parents=True)
            (source_job / "result.json").write_text(
                json.dumps(job_result(1.0)), encoding="utf-8"
            )
            destination = root / "jobs" / "same-name"
            destination.mkdir(parents=True)
            (destination / "result.json").write_text(
                json.dumps(job_result(0.0)), encoding="utf-8"
            )

            with self.assertRaisesRegex(FileExistsError, "--replace"):
                import_harbor_artifact.run(artifact, root / "jobs", replace=False)


if __name__ == "__main__":
    unittest.main()
