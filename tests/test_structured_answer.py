import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "evaluation" / "harbor" / "shared" / "structured_answer.py"
SPEC = importlib.util.spec_from_file_location("structured_answer", ENGINE_PATH)
assert SPEC is not None and SPEC.loader is not None
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


class StructuredAnswerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = {
            "schema_version": "1.0",
            "minimum_characters": 20,
            "groups": {
                "diagnosis": {
                    "root_cause": [[r"\broot\b"], [r"\bcause\b"]],
                    "evidence": [[r"\b(?:log|trace)\b"]],
                }
            },
            "unsupported_claims": [r"\bguessing is enough\b"],
        }

    def test_grouped_patterns_and_guards_score_deterministically(self) -> None:
        scores, details = ENGINE.score_answer(
            "The root cause is supported by a trace and repeatable evidence.", self.rubric
        )

        self.assertEqual(scores["reward"], 1.0)
        self.assertTrue(details["criteria"]["diagnosis"]["root_cause"])

    def test_unsupported_claim_gates_reward(self) -> None:
        scores, _ = ENGINE.score_answer(
            "The root cause has a trace, but guessing is enough for this diagnosis.", self.rubric
        )

        self.assertEqual(scores["reward"], 0.0)

    def test_invalid_rubric_is_rejected(self) -> None:
        rubric = dict(self.rubric)
        rubric["groups"] = {}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rubric.json"
            path.write_text(json.dumps(rubric), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "groups"):
                ENGINE.load_rubric(path)

    def test_all_task_reference_answers_satisfy_their_rubrics(self) -> None:
        tasks_root = ROOT / "evaluation" / "harbor" / "tasks"
        rubrics = sorted(tasks_root.glob("*/tests/rubric.json"))
        self.assertTrue(rubrics)
        for rubric_path in rubrics:
            with self.subTest(task=rubric_path.parents[1].name):
                rubric = ENGINE.load_rubric(rubric_path)
                answer = rubric_path.parents[1] / "solution" / "answer.md"
                scores, details = ENGINE.score_answer(
                    answer.read_text(encoding="utf-8"), rubric
                )
                self.assertEqual(scores["reward"], 1.0, details)
                for criteria in details["criteria"].values():
                    self.assertTrue(all(criteria.values()), details)


if __name__ == "__main__":
    unittest.main()
