from __future__ import annotations

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
