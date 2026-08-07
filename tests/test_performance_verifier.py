import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = (
    ROOT
    / "evaluation"
    / "harbor"
    / "tasks"
    / "performance-tiny-async-gpu-claim"
    / "tests"
    / "check_answer.py"
)
SOLUTION = CHECKER.parents[1] / "solution" / "answer.md"

SPEC = importlib.util.spec_from_file_location("performance_check_answer", CHECKER)
assert SPEC is not None and SPEC.loader is not None
CHECK_ANSWER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_ANSWER)


class PerformanceVerifierTests(unittest.TestCase):
    def test_reference_answer_satisfies_every_criterion(self) -> None:
        scores, details = CHECK_ANSWER.score_answer(SOLUTION.read_text(encoding="utf-8"))

        self.assertEqual(scores["reward"], 1.0)
        for criteria in details["criteria"].values():
            self.assertTrue(all(criteria.values()))
        self.assertEqual(details["unsupported_claim_patterns"], [])

    def test_vague_benchmark_advice_does_not_score_highly(self) -> None:
        answer = (
            "Run more benchmarks with synchronization, representative sizes, and correctness. "
            * 12
        )

        scores, _ = CHECK_ANSWER.score_answer(answer)

        self.assertLess(scores["reward"], 0.35)

    def test_direct_unsupported_claim_is_rejected(self) -> None:
        answer = SOLUTION.read_text(encoding="utf-8") + "\nNo synchronization is needed.\n"

        scores, details = CHECK_ANSWER.score_answer(answer)

        self.assertEqual(scores["reward"], 0.0)
        self.assertTrue(details["unsupported_claim_patterns"])


if __name__ == "__main__":
    unittest.main()
