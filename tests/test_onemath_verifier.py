import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = (
    ROOT
    / "evaluation"
    / "harbor"
    / "tasks"
    / "onemath-runtime-library-missing"
    / "tests"
    / "check_answer.py"
)
SOLUTION = CHECKER.parents[1] / "solution" / "answer.md"

SPEC = importlib.util.spec_from_file_location("onemath_check_answer", CHECKER)
assert SPEC is not None and SPEC.loader is not None
CHECK_ANSWER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_ANSWER)


class OneMathVerifierTests(unittest.TestCase):
    def test_reference_answer_satisfies_every_criterion(self) -> None:
        scores, details = CHECK_ANSWER.score_answer(SOLUTION.read_text(encoding="utf-8"))

        self.assertEqual(scores["reward"], 1.0)
        for criteria in details["criteria"].values():
            self.assertTrue(all(criteria.values()))
        self.assertEqual(details["unsupported_claim_patterns"], [])

    def test_keyword_stuffing_does_not_receive_a_high_score(self) -> None:
        answer = ("runtime dispatch dynamic loader CUDA device. " * 20).strip()

        scores, _ = CHECK_ANSWER.score_answer(answer)

        self.assertLessEqual(scores["reward"], 0.2)

    def test_unsupported_claim_is_penalized(self) -> None:
        answer = SOLUTION.read_text(encoding="utf-8") + "\nLink success guarantees the CUDA backend is usable.\n"

        scores, details = CHECK_ANSWER.score_answer(answer)

        self.assertEqual(scores["unsupported_claim_avoidance"], 0.0)
        self.assertLess(scores["reward"], 1.0)
        self.assertTrue(details["unsupported_claim_patterns"])


if __name__ == "__main__":
    unittest.main()
