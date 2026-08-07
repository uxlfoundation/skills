#!/usr/bin/env python3
"""Deterministic grouped-rubric scorer for Harbor answer-quality tasks."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
from typing import Any


def load_rubric(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"rubric does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"rubric is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("rubric root must be an object")
    if data.get("schema_version") != "1.0":
        raise ValueError("rubric schema_version must be '1.0'")
    minimum = data.get("minimum_characters")
    if not isinstance(minimum, int) or minimum < 1:
        raise ValueError("rubric minimum_characters must be a positive integer")
    groups = data.get("groups")
    if not isinstance(groups, dict) or not groups:
        raise ValueError("rubric groups must be a non-empty object")
    for group_name, criteria in groups.items():
        if not isinstance(group_name, str) or not isinstance(criteria, dict) or not criteria:
            raise ValueError("every rubric group must be a named non-empty object")
        for criterion_name, pattern_groups in criteria.items():
            if not isinstance(criterion_name, str) or not isinstance(pattern_groups, list) or not pattern_groups:
                raise ValueError(f"criterion {group_name}.{criterion_name} must contain pattern groups")
            for patterns in pattern_groups:
                if not isinstance(patterns, list) or not patterns or not all(
                    isinstance(pattern, str) and pattern for pattern in patterns
                ):
                    raise ValueError(
                        f"criterion {group_name}.{criterion_name} pattern groups must be non-empty string arrays"
                    )
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        raise ValueError(
                            f"criterion {group_name}.{criterion_name} has invalid regex {pattern!r}: {exc}"
                        ) from exc
    unsupported = data.get("unsupported_claims", [])
    if not isinstance(unsupported, list) or not all(isinstance(pattern, str) for pattern in unsupported):
        raise ValueError("rubric unsupported_claims must be an array of regex strings")
    for pattern in unsupported:
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValueError(f"unsupported claim has invalid regex {pattern!r}: {exc}") from exc
    return data


def _criterion_matches(text: str, pattern_groups: list[list[str]]) -> bool:
    return all(
        any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)
        for patterns in pattern_groups
    )


def score_answer(
    text: str, rubric: dict[str, Any]
) -> tuple[dict[str, float], dict[str, object]]:
    groups = rubric["groups"]
    criterion_results = {
        group_name: {
            criterion_name: _criterion_matches(text, pattern_groups)
            for criterion_name, pattern_groups in criteria.items()
        }
        for group_name, criteria in groups.items()
    }
    group_scores = {
        group_name: sum(criteria.values()) / len(criteria)
        for group_name, criteria in criterion_results.items()
    }
    unsupported_matches = [
        pattern
        for pattern in rubric.get("unsupported_claims", [])
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    ]
    answer_present = len(text.strip()) >= rubric["minimum_characters"]
    unsupported_claim_avoidance = answer_present and not unsupported_matches
    content_score = sum(group_scores.values()) / len(group_scores)
    reward = content_score * float(unsupported_claim_avoidance)
    scores = {
        "reward": round(reward, 4),
        **{name: round(value, 4) for name, value in group_scores.items()},
        "unsupported_claim_avoidance": float(unsupported_claim_avoidance),
        "answer_present": float(answer_present),
    }
    details: dict[str, object] = {
        "criteria": criterion_results,
        "unsupported_claim_patterns": unsupported_matches,
        "answer_characters": len(text.strip()),
    }
    return scores, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubric", type=Path, default=Path("/tests/rubric.json"))
    parser.add_argument("--answer", type=Path)
    args = parser.parse_args()
    try:
        rubric = load_rubric(args.rubric)
    except ValueError as exc:
        print(f"Rubric error: {exc}")
        return 1
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    answer = args.answer or workspace / "answer.md"
    text = answer.read_text(encoding="utf-8") if answer.exists() else ""
    scores, details = score_answer(text, rubric)
    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scores": scores, **details}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
