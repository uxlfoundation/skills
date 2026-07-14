#!/usr/bin/env python3
"""Materialize deterministic answer arms for evaluator and dashboard smoke tests."""

from __future__ import annotations

import argparse
from pathlib import Path

from run_evals import EvalCase, load_evals


def baseline_answer(case: EvalCase) -> str:
    return (
        f"General response for {case.skill}/{case.eval_id}.\n\n"
        "Review the request, choose an implementation direction, and test the result before merging.\n"
    )


def skill_answer(case: EvalCase) -> str:
    terms = "\n".join(f"- {term}" for term in case.must_include)
    return (
        f"Skill-guided response for {case.skill}/{case.eval_id}.\n\n"
        f"{case.expected_output}\n\n"
        "Coverage terms:\n"
        f"{terms}\n"
    )


def write_answer(root: Path, arm: str, case: EvalCase, text: str) -> None:
    target = root / arm / case.skill / f"{case.eval_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory that will receive baseline/ and skill-explicit/.")
    args = parser.parse_args()

    cases, errors = load_evals()
    if errors:
        print("Eval loading failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    for case in cases:
        write_answer(args.output_dir, "baseline", case, baseline_answer(case))
        write_answer(args.output_dir, "skill-explicit", case, skill_answer(case))

    skills = sorted({case.skill for case in cases})
    print(f"Wrote fixture answer arms for {len(cases)} cases across {len(skills)} skills to {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
