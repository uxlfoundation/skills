import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / "evaluation"
    / "runner-control-repo-template"
    / ".github"
    / "workflows"
    / "intel-gpu-oracle.yml"
)


class RunnerControlTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_only_manual_dispatch_is_configured(self) -> None:
        self.assertIn("  workflow_dispatch:", self.workflow)
        self.assertNotIn("  pull_request:", self.workflow)
        self.assertNotIn("  pull_request_target:", self.workflow)
        self.assertNotIn("  push:", self.workflow)
        self.assertNotIn("  repository_dispatch:", self.workflow)

    def test_requires_a_full_commit_sha_before_checkout(self) -> None:
        self.assertIn("^[0-9a-fA-F]{40}$", self.workflow)
        validation = self.workflow.index("Require an immutable evaluator commit")
        checkout = self.workflow.index("Check out the reviewed evaluator revision")
        self.assertLess(validation, checkout)
        self.assertIn("repository: uxlfoundation/skills", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_all_actions_are_pinned_to_full_commits(self) -> None:
        uses = re.findall(
            r"^\s*(?:-\s*)?uses:\s*([^\s]+)$", self.workflow, re.MULTILINE
        )
        self.assertGreaterEqual(len(uses), 2)
        for action in uses:
            self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$")

    def test_runner_and_container_contract_is_explicit(self) -> None:
        self.assertIn(
            "runs-on: [self-hosted, linux, x64, uxl, sycl, gpu, intel-gpu, personal-lab]",
            self.workflow,
        )
        self.assertIn("test -d /dev/dri", self.workflow)
        self.assertIn("--device /dev/dri:/dev/dri", self.workflow)
        self.assertIn(
            "intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:"
            "e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c",
            self.workflow,
        )

    def test_oracle_gate_and_failure_artifacts_are_required(self) -> None:
        self.assertIn("--agent oracle", self.workflow)
        self.assertIn("--include-task-name sycl-device-discovery", self.workflow)
        self.assertIn("--reward-floor 1.0", self.workflow)
        upload = self.workflow.index("Upload complete Harbor evidence")
        self.assertIn("if: always()", self.workflow[upload : upload + 250])


if __name__ == "__main__":
    unittest.main()
