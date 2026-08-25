import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "harbor-hardware.yml"


class HardwareWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_hardware_workflow_is_manual_only(self) -> None:
        self.assertIn("  workflow_dispatch:", self.workflow)
        self.assertNotIn("  pull_request:", self.workflow)
        self.assertNotIn("  pull_request_target:", self.workflow)
        self.assertNotIn("  push:", self.workflow)

    def test_actions_are_pinned_and_checkout_drops_credentials(self) -> None:
        uses = re.findall(
            r"^\s*(?:-\s*)?uses:\s*([^\s]+)$", self.workflow, re.MULTILINE
        )
        self.assertGreaterEqual(len(uses), 2)
        for action in uses:
            self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$")
        self.assertIn("persist-credentials: false", self.workflow)

    def test_intel_gpu_contract_and_oracle_gate_are_explicit(self) -> None:
        self.assertIn(
            "runs-on: [self-hosted, linux, x64, uxl, sycl, gpu, intel-gpu]",
            self.workflow,
        )
        self.assertIn("--device /dev/dri:/dev/dri", self.workflow)
        self.assertIn("--include-task-name sycl-device-discovery", self.workflow)
        self.assertIn("--job-name uxl-sycl-intel-gpu-oracle", self.workflow)
        self.assertIn("--reward-floor 1.0", self.workflow)

    def test_evidence_upload_runs_after_failures(self) -> None:
        upload = self.workflow.index("actions/upload-artifact@")
        self.assertIn("if: always()", self.workflow[upload : upload + 240])


if __name__ == "__main__":
    unittest.main()
