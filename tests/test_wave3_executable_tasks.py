from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "evaluation" / "harbor" / "tasks"
CASES = (
    ("oneccl-async-allreduce-wait", "async_allreduce_pipeline.py", "async allreduce verifier passed"),
    ("sycl-selector-silent-cpu-fallback", "validate_sycl_run.py", "SYCL device evidence verifier passed"),
    ("performance-floating-reduction-tolerance", "compare_reduction.py", "floating reduction verifier passed"),
)


class Wave3ExecutableTaskTests(unittest.TestCase):
    def run_verifier(self, task: str, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASKS / task / "tests" / "verify.py"), str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def test_oracle_solutions_pass_behavioral_contracts(self) -> None:
        for task, artifact, success_message in CASES:
            with self.subTest(task=task):
                result = self.run_verifier(task, TASKS / task / "solution" / artifact)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(success_message, result.stdout)

    def test_misleading_starters_are_rejected(self) -> None:
        for task, artifact, _ in CASES:
            with self.subTest(task=task):
                result = self.run_verifier(task, TASKS / task / "environment" / artifact)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
