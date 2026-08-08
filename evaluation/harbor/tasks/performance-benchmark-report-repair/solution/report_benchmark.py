#!/usr/bin/env python3
"""Create correctness-gated, scope-specific benchmark comparisons."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


REQUIRED_COLUMNS = {"case", "variant", "seconds", "correct", "warmup", "scope"}
VARIANTS = {"baseline", "candidate"}


def parse_boolean(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{field} must be true or false, got {value!r}")


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain columns {sorted(REQUIRED_COLUMNS)}")
        rows: list[dict[str, Any]] = []
        for line_number, raw in enumerate(reader, start=2):
            variant = raw["variant"].strip()
            case = raw["case"].strip()
            scope = raw["scope"].strip()
            if variant not in VARIANTS:
                raise ValueError(f"line {line_number}: invalid variant {variant!r}")
            if not case or not scope:
                raise ValueError(f"line {line_number}: case and scope must be non-empty")
            try:
                seconds = float(raw["seconds"])
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid seconds") from exc
            rows.append(
                {
                    "case": case,
                    "scope": scope,
                    "variant": variant,
                    "seconds": seconds,
                    "correct": parse_boolean(raw["correct"], "correct"),
                    "warmup": parse_boolean(raw["warmup"], "warmup"),
                }
            )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, object]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["case"], row["scope"]), []).append(row)

    comparisons: list[dict[str, object]] = []
    for (case, scope), group in sorted(grouped.items()):
        measured = [row for row in group if not row["warmup"]]
        by_variant = {
            variant: [row for row in measured if row["variant"] == variant]
            for variant in sorted(VARIANTS)
        }
        comparison: dict[str, object] = {
            "case": case,
            "scope": scope,
            "status": "ok",
            "baseline_samples": len(by_variant["baseline"]),
            "candidate_samples": len(by_variant["candidate"]),
        }
        if any(not row["correct"] for row in measured):
            comparison["status"] = "invalid-correctness"
        elif any(
            not math.isfinite(row["seconds"]) or row["seconds"] <= 0
            for row in measured
        ):
            comparison["status"] = "invalid-timing"
        elif any(len(by_variant[variant]) < 3 for variant in VARIANTS):
            comparison["status"] = "insufficient-samples"
        else:
            baseline = statistics.median(
                row["seconds"] for row in by_variant["baseline"]
            )
            candidate = statistics.median(
                row["seconds"] for row in by_variant["candidate"]
            )
            comparison.update(
                {
                    "baseline_median_seconds": baseline,
                    "candidate_median_seconds": candidate,
                    "speedup": baseline / candidate,
                }
            )
        comparisons.append(comparison)
    return {"schema_version": "1.0", "comparisons": comparisons}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: report_benchmark.py INPUT.csv", file=sys.stderr)
        return 2
    try:
        report = summarize(load_rows(Path(argv[1])))
    except (OSError, ValueError) as exc:
        print(f"benchmark input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
