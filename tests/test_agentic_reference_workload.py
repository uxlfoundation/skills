import json
import subprocess
import sys
import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path

from evaluation.agentic.reference_workload.benchmark import (
    BenchmarkRunner,
    CONTRACT_PATH,
    SerialExecutor,
    ThreadedExecutor,
)


class AgenticReferenceWorkloadTests(unittest.TestCase):
    def test_serial_contract_correctness_and_failure_paths(self):
        runner = BenchmarkRunner.from_path(CONTRACT_PATH, SerialExecutor())
        report = runner.run(repetitions=2, warmups=0)

        self.assertTrue(report["correctness"]["passed"])
        self.assertEqual(
            report["correctness"]["failure_paths"],
            {"pre_cancelled": "pass", "tool_exception": "pass"},
        )
        self.assertEqual(set(report["scenarios"]), {"short-turn", "tool-fan-out", "retrieval-heavy"})

    def test_threaded_executor_preserves_results(self):
        runner = BenchmarkRunner.from_path(CONTRACT_PATH, ThreadedExecutor(max_workers=4))
        report = runner.run(repetitions=2, warmups=0)

        self.assertTrue(report["correctness"]["passed"])
        fanout = [run for run in report["runs"] if run["scenario_id"] == "tool-fan-out"]
        self.assertTrue(all(run["answer"].startswith("oneDAL=incubating") for run in fanout))

    @unittest.skipUnless(find_spec("langgraph"), "optional LangGraph dependency is not installed")
    def test_langgraph_adapter_preserves_contract(self):
        from evaluation.agentic.reference_workload.langgraph_adapter import LangGraphExecutor

        runner = BenchmarkRunner.from_path(CONTRACT_PATH, LangGraphExecutor(max_workers=4))
        report = runner.run(repetitions=1, warmups=0)
        self.assertTrue(report["correctness"]["passed"])
        self.assertEqual(report["executor"], "langgraph")
        self.assertEqual(report["configuration"]["external_dependencies"], 1)

    @unittest.skipUnless(find_spec("onedal"), "optional oneDAL dependency is not installed")
    def test_onedal_retriever_preserves_routes(self):
        from evaluation.agentic.reference_workload.onedal_retriever import OnedalRetriever

        runner = BenchmarkRunner.from_path(CONTRACT_PATH, SerialExecutor(), OnedalRetriever())
        report = runner.run(repetitions=1, warmups=0)
        self.assertTrue(report["correctness"]["passed"])
        self.assertEqual(report["retriever"], "onedal")
        self.assertGreaterEqual(report["configuration"]["retriever_setup_ms"], 0)

    def test_cli_writes_machine_readable_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "evaluation.agentic.reference_workload",
                    "--executor",
                    "serial",
                    "--repetitions",
                    "1",
                    "--warmups",
                    "0",
                    "--summary-only",
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertNotIn("runs", report)
            self.assertTrue(report["correctness"]["passed"])


if __name__ == "__main__":
    unittest.main()
