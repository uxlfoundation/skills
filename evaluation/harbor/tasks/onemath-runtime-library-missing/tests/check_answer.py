#!/usr/bin/env python3
"""Score a oneMath runtime-backend diagnostic answer deterministically."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Final


CRITERIA: Final[dict[str, dict[str, tuple[tuple[str, ...], ...]]]] = {
    "diagnosis": {
        "dispatch_distinction": (
            (r"\bruntime[- ]+dispatch\b",),
            (r"\blink(?:ing|-time|er|ed)?\b",),
            (
                r"\b(?:does\s+not|doesn't|cannot|can't)\s+(?:prove|guarantee|establish)\b",
                r"\bonly\s+(?:confirms?|shows?|proves?)\b",
            ),
        ),
        "domain_backend": (
            (r"\b(?:blas|lapack|rng|dft|sparse|gemm|fft)\b",),
            (r"\b(?:cublas|cusolver|curand|cufft|cusparse)\b",),
        ),
        "backend_deployment": (
            (r"\b(?:backend|plugin|wrapper)\b",),
            (r"\b(?:built|build|enabled?|installed?|deployed?|available|absent|missing)\b",),
            (r"\b(?:library|libraries|shared\s+objects?|\.so)\b",),
        ),
    },
    "evidence": {
        "loader_evidence": (
            (r"\b(?:ldd|ld_debug|loader|dynamic\s+linker)\b",),
            (r"\b(?:rpath|runpath|ld_library_path|search\s+path)\b",),
            (r"\b(?:wrapper|plugin|backend|shared\s+librar(?:y|ies))\b",),
        ),
        "device_evidence": (
            (r"\b(?:queue|device|selector)\b",),
            (r"\b(?:vendor|backend|platform)\b",),
            (r"\b(?:sycl-ls|nvidia-smi|device\s+enumeration)\b",),
        ),
        "compatibility_evidence": (
            (r"\b(?:support(?:ed)?\s+matrix|compatib\w*|supported\s+configuration)\b",),
            (r"\b(?:cuda|driver)\b",),
            (r"\b(?:compiler|abi|version)\b",),
        ),
    },
    "validation": {
        "known_answer_validation": (
            (r"\b(?:minimal|small)\b",),
            (r"\b(?:known[- ]answer|reference|compare)\b",),
            (r"\b(?:cpu|expected)\b",),
        ),
        "async_validation": (
            (r"\b(?:wait_and_throw|wait\s+and\s+throw|event\w*\s+wait|queue\w*\s+wait)\b",),
            (r"\b(?:asynchronous|async|exception|error)\b",),
        ),
        "execution_validation": (
            (r"\b(?:profiler|profile|trace|nsys|vtune)\b",),
            (r"\b(?:representative|production|realistic)\b",),
            (r"\b(?:size|workload|benchmark|warm[- ]?up|timing|performance)\b",),
        ),
    },
}

UNSUPPORTED_CLAIMS: Final[tuple[str, ...]] = (
    r"\blink\s+success\s+(?:is\s+enough|guarantees?)\b",
    r"\blink\s+success\s+proves?\s+(?!only\b)",
    r"\b(?:gpu_selector|gpu\s+selector)\s+(?:alone\s+)?(?:proves?|guarantees?)\b",
    r"\b(?:all|every)\s+(?:onemath\s+)?(?:domains?|backends?)\s+(?:are|is)\s+(?:available|supported|guaranteed)\b",
)


def _criterion_matches(text: str, pattern_groups: tuple[tuple[str, ...], ...]) -> bool:
    """Require at least one regex match from every evidence group."""
    return all(
        any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in group)
        for group in pattern_groups
    )


def score_answer(text: str) -> tuple[dict[str, float], dict[str, object]]:
    """Return Harbor metrics and human-readable criterion diagnostics."""
    criterion_results = {
        group: {
            name: _criterion_matches(text, pattern_groups)
            for name, pattern_groups in criteria.items()
        }
        for group, criteria in CRITERIA.items()
    }
    group_scores = {
        group: sum(results.values()) / len(results)
        for group, results in criterion_results.items()
    }
    unsupported_matches = [
        pattern
        for pattern in UNSUPPORTED_CLAIMS
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    ]
    answer_present = len(text.strip()) >= 400
    unsupported_claim_avoidance = answer_present and not unsupported_matches
    component_scores: dict[str, float] = {
        **group_scores,
        "unsupported_claim_avoidance": float(unsupported_claim_avoidance),
        "answer_present": float(answer_present),
    }
    content_score = sum(group_scores.values()) / len(group_scores)
    reward = content_score * float(unsupported_claim_avoidance) * float(answer_present)
    scores = {
        "reward": round(reward, 4),
        **{name: round(value, 4) for name, value in component_scores.items()},
    }
    details: dict[str, object] = {
        "criteria": criterion_results,
        "unsupported_claim_patterns": unsupported_matches,
        "answer_characters": len(text.strip()),
    }
    return scores, details


def main() -> int:
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    path = workspace / "answer.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    scores, details = score_answer(text)
    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scores": scores, **details}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
