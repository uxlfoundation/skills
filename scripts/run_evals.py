#!/usr/bin/env python3
"""Validate, emit, and score UXL skill eval prompts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


@dataclass(frozen=True)
class EvalCase:
    skill: str
    eval_id: str
    prompt: str
    expected_output: str
    must_include: tuple[str, ...]
    must_not_include: tuple[str, ...]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold())


def load_evals() -> tuple[list[EvalCase], list[str]]:
    cases: list[EvalCase] = []
    errors: list[str] = []
    for eval_file in sorted(SKILLS.glob("*/evals/evals.json")):
        try:
            data = json.loads(eval_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{eval_file}: invalid JSON: {exc}")
            continue

        skill_name = data.get("skill_name")
        if skill_name != eval_file.parents[1].name:
            errors.append(f"{eval_file}: skill_name must match skill directory")
            continue

        evals = data.get("evals")
        if not isinstance(evals, list) or not evals:
            errors.append(f"{eval_file}: evals must be a non-empty list")
            continue

        seen: set[str] = set()
        for item in evals:
            if not isinstance(item, dict):
                errors.append(f"{eval_file}: eval entries must be objects")
                continue
            missing = [key for key in ("id", "prompt", "expected_output", "checks") if key not in item]
            if missing:
                errors.append(f"{eval_file}: eval missing {', '.join(missing)}")
                continue
            eval_id = item["id"]
            if eval_id in seen:
                errors.append(f"{eval_file}: duplicate eval id {eval_id}")
                continue
            seen.add(eval_id)
            checks = item["checks"]
            if not isinstance(checks, dict):
                errors.append(f"{eval_file}: checks must be an object for {eval_id}")
                continue
            must_include = checks.get("must_include")
            must_not_include = checks.get("must_not_include", [])
            if not isinstance(must_include, list) or not must_include:
                errors.append(f"{eval_file}: checks.must_include must be a non-empty list for {eval_id}")
                continue
            if not isinstance(must_not_include, list):
                errors.append(f"{eval_file}: checks.must_not_include must be a list for {eval_id}")
                continue
            cases.append(
                EvalCase(
                    skill=skill_name,
                    eval_id=eval_id,
                    prompt=item["prompt"],
                    expected_output=item["expected_output"],
                    must_include=tuple(str(term) for term in must_include),
                    must_not_include=tuple(str(term) for term in must_not_include),
                )
            )
    return cases, errors


def answer_path(answers_dir: Path, case: EvalCase) -> Path | None:
    candidates = [
        answers_dir / case.skill / f"{case.eval_id}.md",
        answers_dir / case.skill / f"{case.eval_id}.txt",
        answers_dir / f"{case.skill}--{case.eval_id}.md",
        answers_dir / f"{case.skill}--{case.eval_id}.txt",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def score_answer(answer: str, case: EvalCase) -> tuple[float, list[str]]:
    normalized = normalize(answer)
    misses = [term for term in case.must_include if normalize(term) not in normalized]
    forbidden = [term for term in case.must_not_include if normalize(term) in normalized]
    total_checks = len(case.must_include) + len(case.must_not_include)
    failed = len(misses) + len(forbidden)
    score = 1.0 if total_checks == 0 else (total_checks - failed) / total_checks
    notes = [f"missing: {term}" for term in misses] + [f"forbidden: {term}" for term in forbidden]
    return score, notes


def write_prompts(cases: list[EvalCase], output_dir: Path) -> None:
    for case in cases:
        target_dir = output_dir / case.skill
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{case.eval_id}.md"
        target.write_text(
            f"# {case.skill} / {case.eval_id}\n\n{case.prompt}\n\n## Expected rubric\n\n{case.expected_output}\n",
            encoding="utf-8",
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="Validate eval definitions and exit.")
    parser.add_argument("--list", action="store_true", help="List eval cases.")
    parser.add_argument("--write-prompts", type=Path, help="Write prompt markdown files to a directory.")
    parser.add_argument("--answers-dir", type=Path, help="Score answers from a directory.")
    parser.add_argument("--fail-under", type=float, default=1.0, help="Minimum average score when scoring answers.")
    args = parser.parse_args(argv)

    cases, errors = load_evals()
    if errors:
        print("Eval validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.validate:
        print(f"Eval validation passed: {len(cases)} cases.")

    if args.list:
        for case in cases:
            print(f"{case.skill}/{case.eval_id}: {case.prompt}")

    if args.write_prompts:
        write_prompts(cases, args.write_prompts)
        print(f"Wrote {len(cases)} prompts to {args.write_prompts}")

    if args.answers_dir:
        scores: list[float] = []
        missing_answers: list[str] = []
        for case in cases:
            path = answer_path(args.answers_dir, case)
            if not path:
                missing_answers.append(f"{case.skill}/{case.eval_id}")
                scores.append(0.0)
                continue
            score, notes = score_answer(path.read_text(encoding="utf-8"), case)
            scores.append(score)
            detail = "; ".join(notes) if notes else "pass"
            print(f"{case.skill}/{case.eval_id}: {score:.2f} {detail}")

        if missing_answers:
            print("Missing answers:", file=sys.stderr)
            for item in missing_answers:
                print(f"- {item}", file=sys.stderr)
        average = sum(scores) / len(scores) if scores else 0.0
        print(f"Average score: {average:.2f}")
        if average < args.fail_under:
            return 1

    if not any((args.validate, args.list, args.write_prompts, args.answers_dir)):
        print(f"Eval validation passed: {len(cases)} cases.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
