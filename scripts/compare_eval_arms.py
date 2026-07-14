#!/usr/bin/env python3
"""Compare baseline and skill-assisted eval answer directories."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from run_evals import EvalCase, answer_path, load_evals, score_answer


def parse_skill_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    skills: set[str] = set()
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                skills.add(item)
    return skills or None


def score_case(answers_dir: Path, case: EvalCase) -> dict:
    path = answer_path(answers_dir, case)
    if path is None:
        return {
            "path": None,
            "score": 0.0,
            "notes": ["missing answer"],
            "missing": True,
            "forbidden_hits": 0,
        }
    score, notes = score_answer(path.read_text(encoding="utf-8"), case)
    return {
        "path": str(path),
        "score": score,
        "notes": notes,
        "missing": False,
        "forbidden_hits": sum(1 for note in notes if note.startswith("forbidden:")),
    }


def round_score(value: float) -> float:
    return round(value, 4)


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_report(
    cases: list[EvalCase],
    baseline_dir: Path,
    skill_dir: Path,
    label: str,
) -> dict:
    case_reports: list[dict] = []
    by_skill: dict[str, dict] = {}

    for case in cases:
        baseline = score_case(baseline_dir, case)
        skill = score_case(skill_dir, case)
        delta = skill["score"] - baseline["score"]
        case_report = {
            "skill": case.skill,
            "eval_id": case.eval_id,
            "prompt": case.prompt,
            "expected_output": case.expected_output,
            "baseline": baseline,
            "skill_explicit": skill,
            "delta": round_score(delta),
        }
        case_reports.append(case_report)

        bucket = by_skill.setdefault(
            case.skill,
            {
                "skill": case.skill,
                "cases": 0,
                "baseline_scores": [],
                "skill_scores": [],
                "deltas": [],
                "skill_wins": 0,
                "skill_losses": 0,
                "ties": 0,
                "missing_baseline": 0,
                "missing_skill": 0,
                "skill_forbidden_hits": 0,
            },
        )
        bucket["cases"] += 1
        bucket["baseline_scores"].append(baseline["score"])
        bucket["skill_scores"].append(skill["score"])
        bucket["deltas"].append(delta)
        bucket["missing_baseline"] += int(baseline["missing"])
        bucket["missing_skill"] += int(skill["missing"])
        bucket["skill_forbidden_hits"] += skill["forbidden_hits"]
        if delta > 0:
            bucket["skill_wins"] += 1
        elif delta < 0:
            bucket["skill_losses"] += 1
        else:
            bucket["ties"] += 1

    skill_summaries: list[dict] = []
    for bucket in sorted(by_skill.values(), key=lambda item: item["skill"]):
        summary = {
            "skill": bucket["skill"],
            "cases": bucket["cases"],
            "baseline_average": round_score(average(bucket["baseline_scores"])),
            "skill_average": round_score(average(bucket["skill_scores"])),
            "delta": round_score(average(bucket["deltas"])),
            "skill_wins": bucket["skill_wins"],
            "skill_losses": bucket["skill_losses"],
            "ties": bucket["ties"],
            "missing_baseline": bucket["missing_baseline"],
            "missing_skill": bucket["missing_skill"],
            "skill_forbidden_hits": bucket["skill_forbidden_hits"],
        }
        skill_summaries.append(summary)

    all_baseline = [case["baseline"]["score"] for case in case_reports]
    all_skill = [case["skill_explicit"]["score"] for case in case_reports]
    all_delta = [case["delta"] for case in case_reports]
    summary = {
        "label": label,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "case_count": len(case_reports),
        "skill_count": len(skill_summaries),
        "baseline_average": round_score(average(all_baseline)),
        "skill_average": round_score(average(all_skill)),
        "delta": round_score(average(all_delta)),
        "skill_wins": sum(1 for case in case_reports if case["delta"] > 0),
        "skill_losses": sum(1 for case in case_reports if case["delta"] < 0),
        "ties": sum(1 for case in case_reports if case["delta"] == 0),
        "missing_baseline": sum(1 for case in case_reports if case["baseline"]["missing"]),
        "missing_skill": sum(1 for case in case_reports if case["skill_explicit"]["missing"]),
        "skill_forbidden_hits": sum(case["skill_explicit"]["forbidden_hits"] for case in case_reports),
    }

    return {
        "schema_version": "0",
        "label": label,
        "arms": {
            "baseline": str(baseline_dir),
            "skill_explicit": str(skill_dir),
        },
        "summary": summary,
        "skills": skill_summaries,
        "cases": case_reports,
    }


def markdown_report(report: dict) -> str:
    summary = report["summary"]
    lines = [
        f"# UXL Skill Eval Scorecard: {summary['label']}",
        "",
        "## Summary",
        "",
        "| Cases | Skills | Baseline avg | Skill avg | Delta | Wins | Losses | Ties | Missing skill answers | Skill forbidden hits |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {summary['case_count']} | {summary['skill_count']} | "
            f"{summary['baseline_average']:.4f} | {summary['skill_average']:.4f} | "
            f"{summary['delta']:+.4f} | {summary['skill_wins']} | {summary['skill_losses']} | "
            f"{summary['ties']} | {summary['missing_skill']} | {summary['skill_forbidden_hits']} |"
        ),
        "",
        "## By Skill",
        "",
        "| Skill | Cases | Baseline avg | Skill avg | Delta | Wins | Losses | Ties | Missing skill | Forbidden hits |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for skill in report["skills"]:
        lines.append(
            f"| `{skill['skill']}` | {skill['cases']} | {skill['baseline_average']:.4f} | "
            f"{skill['skill_average']:.4f} | {skill['delta']:+.4f} | {skill['skill_wins']} | "
            f"{skill['skill_losses']} | {skill['ties']} | {skill['missing_skill']} | "
            f"{skill['skill_forbidden_hits']} |"
        )

    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| Skill | Eval | Baseline | Skill | Delta | Skill notes |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for case in report["cases"]:
        notes = "; ".join(case["skill_explicit"]["notes"]) if case["skill_explicit"]["notes"] else "pass"
        notes = notes.replace("|", "\\|")
        lines.append(
            f"| `{case['skill']}` | `{case['eval_id']}` | {case['baseline']['score']:.4f} | "
            f"{case['skill_explicit']['score']:.4f} | {case['delta']:+.4f} | {notes} |"
        )

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, required=True, help="Answers from the no-skill baseline arm.")
    parser.add_argument("--skill-dir", type=Path, required=True, help="Answers from the skill_explicit arm.")
    parser.add_argument("--output-dir", type=Path, help="Directory for scorecard.json and scorecard.md.")
    parser.add_argument("--label", default="manual", help="Human-readable report label.")
    parser.add_argument("--skill", action="append", help="Skill filter. May be repeated or comma-separated.")
    parser.add_argument("--eval", action="append", help="Eval id filter. May be repeated or comma-separated.")
    parser.add_argument("--allow-missing", action="store_true", help="Do not fail when answers are missing.")
    parser.add_argument("--fail-under-skill-score", type=float, help="Minimum overall skill arm average.")
    parser.add_argument("--fail-under-delta", type=float, help="Minimum overall skill delta.")
    args = parser.parse_args(argv)

    cases, errors = load_evals()
    if errors:
        print("Eval validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill_filter = parse_skill_filter(args.skill)
    if skill_filter is not None:
        cases = [case for case in cases if case.skill in skill_filter]
        missing_skills = sorted(skill_filter.difference({case.skill for case in cases}))
        if missing_skills:
            print(f"No eval cases found for skills: {', '.join(missing_skills)}", file=sys.stderr)
            return 1

    eval_filter = parse_skill_filter(args.eval)
    if eval_filter is not None:
        cases = [case for case in cases if case.eval_id in eval_filter]
        missing_evals = sorted(eval_filter.difference({case.eval_id for case in cases}))
        if missing_evals:
            print(f"No eval cases found for ids: {', '.join(missing_evals)}", file=sys.stderr)
            return 1

    if not cases:
        print("No eval cases selected.", file=sys.stderr)
        return 1

    report = build_report(cases, args.baseline_dir, args.skill_dir, args.label)
    markdown = markdown_report(report)

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "scorecard.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "scorecard.md").write_text(markdown, encoding="utf-8")

    print(markdown)

    summary = report["summary"]
    failed = False
    if not args.allow_missing and (summary["missing_baseline"] or summary["missing_skill"]):
        print("Missing answers detected. Use --allow-missing for exploratory reports.", file=sys.stderr)
        failed = True
    if args.fail_under_skill_score is not None and summary["skill_average"] < args.fail_under_skill_score:
        print(
            f"Skill average {summary['skill_average']:.4f} is below {args.fail_under_skill_score:.4f}.",
            file=sys.stderr,
        )
        failed = True
    if args.fail_under_delta is not None and summary["delta"] < args.fail_under_delta:
        print(f"Skill delta {summary['delta']:+.4f} is below {args.fail_under_delta:+.4f}.", file=sys.stderr)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
