#!/usr/bin/env python3
"""Score deterministic answer-quality checks for the oneMath pilot."""

from __future__ import annotations

import json
import os
from pathlib import Path


REQUIRED = ["runtime dispatch", "dynamic", "loader", "CUDA", "device"]
FORBIDDEN = ["link success is enough", "compile-time only"]


def main() -> int:
    workspace = Path(os.environ.get("UXL_WORKSPACE", "/app"))
    path = workspace / "answer.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    folded = text.casefold()
    required_hits = sum(term.casefold() in folded for term in REQUIRED)
    forbidden_hits = sum(term.casefold() in folded for term in FORBIDDEN)
    answer_present = len(text.strip()) >= 120
    unsupported_claim_avoidance = answer_present and forbidden_hits == 0
    scores = {
        "reward": round((required_hits / len(REQUIRED) + unsupported_claim_avoidance + answer_present) / 3, 4),
        "required_terms": round(required_hits / len(REQUIRED), 4),
        "unsupported_claim_avoidance": float(unsupported_claim_avoidance),
        "answer_present": float(answer_present),
    }
    log_dir = Path(os.environ.get("UXL_VERIFIER_LOGS", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "reward.json").write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"required_hits": required_hits, "forbidden_hits": forbidden_hits, **scores}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
