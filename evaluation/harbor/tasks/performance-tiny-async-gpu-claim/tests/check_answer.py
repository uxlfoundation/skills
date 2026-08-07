#!/usr/bin/env python3
"""Score a performance-claim review and replacement benchmark plan."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Final


CRITERIA: Final[dict[str, dict[str, tuple[tuple[str, ...], ...]]]] = {
    "correctness": {
        "rejects_claim": (
            (r"\b(?:under[- ]supported|unsupported|invalid|withdraw|not\s+(?:supported|justified))\b",),
            (r"\b(?:single|one)\b",),
            (r"\b(?:tiny|1,?024|small)\b",),
        ),
        "reference_and_tolerance": (
            (r"\b(?:reference|expected|baseline)\b",),
            (r"\b(?:compare|comparison|parity|correctness)\b",),
            (r"\b(?:tolerance|exact|equality)\b",),
        ),
        "async_completion": (
            (r"\b(?:event|queue|asynchronous|async)\b",),
            (r"\b(?:wait|synchroniz\w*)\b",),
            (r"\b(?:submission|enqueue|completion|completed)\b",),
        ),
    },
    "measurement": {
        "representative_sizes": (
            (r"\b(?:representative|production)\b",),
            (r"\b(?:sizes?|sweep|range)\b",),
            (r"\b(?:crossover|small|tiny)\b",),
        ),
        "timing_boundaries": (
            (r"\b(?:allocation|setup)\b",),
            (r"\b(?:transfer|data\s+movement)\b",),
            (r"\bwarm[- ]?up\b",),
            (r"\b(?:steady[- ]state|kernel|compute)\b",),
            (r"\b(?:end[- ]to[- ]end|teardown)\b",),
        ),
        "repetitions_and_variance": (
            (r"\b(?:iterations?|repetitions?|runs?|samples?)\b",),
            (r"\b(?:median|mean|percentile)\b",),
            (r"\b(?:variance|standard\s+deviation|dispersion|outliers?)\b",),
        ),
    },
    "reporting": {
        "environment_evidence": (
            (r"\b(?:GPU|device)\b",),
            (r"\bCPU\b",),
            (r"\b(?:driver|runtime)\b",),
            (r"\b(?:compiler|build|optimization)\b",),
        ),
        "fair_baseline_and_profile": (
            (r"\b(?:optimized|fair|same\s+work)\b",),
            (r"\bCPU\s+baseline\b|\bbaseline\s+CPU\b",),
            (r"\b(?:profiler|profile|trace|timeline)\b",),
            (r"\b(?:repeatable|reproducible)\b",),
        ),
        "bounded_claim": (
            (r"\b(?:tested|measured)\b",),
            (r"\b(?:hardware|environment|configuration)\b",),
            (r"\b(?:limitations?|scope|kernel[- ]only|end[- ]to[- ]end)\b",),
            (r"\b(?:claim|speedup|faster)\b",),
        ),
    },
}

UNSUPPORTED_CLAIMS: Final[tuple[str, ...]] = (
    r"\b(?:single|one)\s+(?:tiny|small)\s+(?:input|run).{0,50}\bproves?\b",
    r"\b(?:submission|enqueue)\s+tim(?:e|ing).{0,50}\bproves?\b",
    r"\bno\s+(?:wait|synchronization)\s+(?:is\s+)?needed\b",
    r"(?:^|\n)\s*(?:[-*]\s*)?guaranteed\s+(?:speedup|faster|performance)\b",
)


def _matches(text: str, groups: tuple[tuple[str, ...], ...]) -> bool:
    return all(
        any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in group)
        for group in groups
    )


def score_answer(text: str) -> tuple[dict[str, float], dict[str, object]]:
    results = {
        group: {name: _matches(text, patterns) for name, patterns in criteria.items()}
        for group, criteria in CRITERIA.items()
    }
    group_scores = {
        group: sum(criteria.values()) / len(criteria) for group, criteria in results.items()
    }
    unsupported = [
        pattern
        for pattern in UNSUPPORTED_CLAIMS
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    ]
    answer_present = len(text.strip()) >= 500
    avoidance = answer_present and not unsupported
    reward = (sum(group_scores.values()) / len(group_scores)) * float(avoidance)
    scores = {
        "reward": round(reward, 4),
        **{name: round(value, 4) for name, value in group_scores.items()},
        "unsupported_claim_avoidance": float(avoidance),
        "answer_present": float(answer_present),
    }
    details: dict[str, object] = {
        "criteria": results,
        "unsupported_claim_patterns": unsupported,
        "answer_characters": len(text.strip()),
    }
    return scores, details


def main() -> int:
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    answer = workspace / "answer.md"
    text = answer.read_text(encoding="utf-8") if answer.exists() else ""
    scores, details = score_answer(text)
    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scores": scores, **details}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
