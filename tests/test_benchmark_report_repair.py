from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "evaluation" / "harbor" / "tasks" / "performance-benchmark-report-repair"
VERIFIER = TASK / "tests" / "verify.py"
SOLUTION = TASK / "solution" / "report_benchmark.py"
STARTER = TASK / "environment" / "report_benchmark.py"


class BenchmarkReportRepairTests(unittest.TestCase):
    def run_verifier(self, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VERIFIER), str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def test_oracle_passes_behavioral_contract(self) -> None:
        result = self.run_verifier(SOLUTION)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("verifier passed", result.stdout)

    def test_misleading_starter_is_rejected(self) -> None:
        result = self.run_verifier(STARTER)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
