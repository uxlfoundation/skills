from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "evaluation" / "runner-control-repo-template" / ".github" / "workflows" / "specialized-target-oracle.yml"
sys.path.insert(0, str(ROOT / "scripts" / "runner"))

import run_target_adapter as adapter  # noqa: E402


def valid_config() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "adapter_id": "example-target-gpu",
        "task": {
            "skill": "uxl-sycl-build-debug",
            "name": "sycl-device-discovery",
            "hardware_class": "target-gpu",
        },
        "runner": {
            "required_labels": ["self-hosted", "linux", "x64", "target-gpu"]
        },
        "probes": [
            {
                "id": "device-enumeration",
                "command": [sys.executable, "-c", "print('target ready')"],
                "timeout_seconds": 10,
                "required_patterns": ["target ready"],
                "publish_output": False,
            }
        ],
        "harbor": {
            "command": ["harbor"],
            "timeout_seconds": 3600,
            "environment": {"UXL_TARGET_ADAPTER": "example-target-gpu"},
        },
    }


class TargetAdapterTests(unittest.TestCase):
    def test_generic_dispatcher_is_manual_pinned_and_approval_gated(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("approved-commits.txt", workflow)
        self.assertIn("merge-base --is-ancestor", workflow)
        self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")
        self.assertRegex(workflow, r"actions/upload-artifact@[0-9a-f]{40}")
        self.assertIn("run_target_adapter.py", workflow)

    def test_validates_portable_adapter(self) -> None:
        self.assertEqual(adapter.validate_adapter(valid_config()), [])

    def test_rejects_secret_environment_and_duplicate_probe(self) -> None:
        config = valid_config()
        harbor = config["harbor"]
        assert isinstance(harbor, dict)
        harbor["environment"] = {"API_TOKEN": "do-not-store"}
        probes = config["probes"]
        assert isinstance(probes, list)
        probes.append(copy.deepcopy(probes[0]))

        errors = adapter.validate_adapter(config)

        self.assertTrue(any("secrets are not allowed" in error for error in errors))
        self.assertTrue(any("duplicate probe id" in error for error in errors))

    def test_probe_records_digest_without_output_by_default(self) -> None:
        config = valid_config()
        probe = config["probes"][0]
        assert isinstance(probe, dict)
        with tempfile.TemporaryDirectory() as directory:
            result = adapter.run_probe(probe, Path(directory), {})

        self.assertTrue(result["passed"])
        self.assertNotIn("output", result)
        self.assertRegex(str(result["output_sha256"]), r"^[0-9a-f]{64}$")

    def test_builds_fixed_oracle_command(self) -> None:
        config = valid_config()
        command = adapter.build_harbor_command(
            config, Path("/repo"), Path("/results/jobs"), "example-oracle"
        )

        self.assertIn("oracle", command)
        self.assertIn("sycl-device-discovery", command)
        self.assertEqual(command[command.index("--n-attempts") + 1], "1")

    def test_cli_validate_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "target-adapter.json"
            path.write_text(json.dumps(valid_config()), encoding="utf-8")
            with redirect_stdout(sys.stdout), redirect_stderr(sys.stderr):
                exit_code = adapter.main(
                    [
                        "--config",
                        str(path),
                        "--source-root",
                        str(ROOT),
                        "--expected-commit",
                        "1" * 40,
                        "--output",
                        str(Path(directory) / "results"),
                        "--validate-only",
                    ]
                )
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
