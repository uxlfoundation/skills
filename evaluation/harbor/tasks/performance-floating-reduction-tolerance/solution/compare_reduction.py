#!/usr/bin/env python3
"""Compare floating-point reductions with combined absolute/relative tolerance."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any


FIELDS = {"reference", "candidate", "atol", "rtol"}


def finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def load_input(path: Path) -> tuple[list[float], list[float], float, float]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read input: {exc}") from exc
    if not isinstance(raw, dict) or set(raw) != FIELDS:
        raise ValueError(f"input must contain exactly {sorted(FIELDS)}")
    if not isinstance(raw["reference"], list) or not isinstance(raw["candidate"], list):
        raise ValueError("reference and candidate must be arrays")
    if not raw["reference"] or len(raw["reference"]) != len(raw["candidate"]):
        raise ValueError("reference and candidate must be non-empty and equal length")

    reference = [finite_number(value, f"reference[{index}]") for index, value in enumerate(raw["reference"])]
    candidate = [finite_number(value, f"candidate[{index}]") for index, value in enumerate(raw["candidate"])]
    atol = finite_number(raw["atol"], "atol")
    rtol = finite_number(raw["rtol"], "rtol")
    if atol < 0 or rtol < 0:
        raise ValueError("atol and rtol must be non-negative")
    return reference, candidate, atol, rtol


def compare(reference: list[float], candidate: list[float], atol: float, rtol: float) -> dict[str, object]:
    errors = [abs(actual - expected) for expected, actual in zip(reference, candidate)]
    mismatches = sum(
        error > atol + rtol * abs(expected)
        for expected, error in zip(reference, errors)
    )
    max_error = max(errors)
    return {
        "schema_version": "1.0",
        "status": "pass" if mismatches == 0 else "fail",
        "sample_count": len(reference),
        "mismatch_count": mismatches,
        "atol": atol,
        "rtol": rtol,
        "max_absolute_error": max_error,
        "worst_index": errors.index(max_error),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: compare_reduction.py INPUT.json", file=sys.stderr)
        return 2
    try:
        report = compare(*load_input(Path(argv[1])))
    except ValueError as exc:
        print(f"reduction input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
