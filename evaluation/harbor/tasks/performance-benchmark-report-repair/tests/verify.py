#!/usr/bin/env python3
"""Behavioral verifier for the benchmark report repair task."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


FIELDS = ["case", "variant", "seconds", "correct", "warmup", "scope"]


def row(case: str, variant: str, seconds: object, *, correct: bool = True, warmup: bool = False, scope: str = "end-to-end") -> dict[str, object]:
    return {
        "case": case,
        "variant": variant,
        "seconds": seconds,
        "correct": str(correct).lower(),
        "warmup": str(warmup).lower(),
        "scope": scope,
    }


def run_report(script: Path, rows: list[dict[str, object]]) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as directory:
        csv_path = Path(directory) / "runs.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        result = subprocess.run(
            [sys.executable, str(script), str(csv_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    if result.returncode != 0:
        raise AssertionError(f"report failed: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"stdout is not one JSON document: {result.stdout!r}") from exc


def comparison_map(report: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    assert report.get("schema_version") == "1.0", report
    raw = report.get("comparisons")
    assert isinstance(raw, list), report
    pairs = [(item.get("case"), item.get("scope")) for item in raw if isinstance(item, dict)]
    assert pairs == sorted(pairs), pairs
    assert len(pairs) == len(set(pairs)), pairs
    return {(str(item["case"]), str(item["scope"])): item for item in raw}


def assert_no_claim(item: dict[str, object], status: str) -> None:
    assert item.get("status") == status, item
    assert "speedup" not in item, item
    assert "baseline_median_seconds" not in item, item
    assert "candidate_median_seconds" not in item, item


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: verify.py SCRIPT")
    script = Path(argv[1])
    rows: list[dict[str, object]] = []

    for value in (999, 10, 12, 11):
        rows.append(row("axpy", "baseline", value, warmup=value == 999))
    for value in (777, 5, 7, 6):
        rows.append(row("axpy", "candidate", value, warmup=value == 777))
    for value in (4, 6, 5):
        rows.append(row("axpy", "baseline", value, scope="kernel"))
    for value in (2, 3, 2.5):
        rows.append(row("axpy", "candidate", value, scope="kernel"))

    for value in (8, 9, 10):
        rows.append(row("bad-output", "baseline", value))
    rows.extend(
        [
            row("bad-output", "candidate", 4),
            row("bad-output", "candidate", 5, correct=False),
            row("bad-output", "candidate", 6),
        ]
    )

    for value in (3, 4, 5):
        rows.append(row("short", "baseline", value))
    rows.extend([row("short", "candidate", 2), row("short", "candidate", 2.5)])
    rows.append(row("short", "candidate", 100, warmup=True))

    for value in (2, 3, 4):
        rows.append(row("bad-clock", "baseline", value))
    rows.extend(
        [row("bad-clock", "candidate", 1), row("bad-clock", "candidate", 0), row("bad-clock", "candidate", 1.5)]
    )

    report = run_report(script, rows)
    items = comparison_map(report)
    assert set(items) == {
        ("axpy", "end-to-end"),
        ("axpy", "kernel"),
        ("bad-clock", "end-to-end"),
        ("bad-output", "end-to-end"),
        ("short", "end-to-end"),
    }, items

    end_to_end = items[("axpy", "end-to-end")]
    assert end_to_end.get("status") == "ok", end_to_end
    assert end_to_end.get("baseline_samples") == 3, end_to_end
    assert end_to_end.get("candidate_samples") == 3, end_to_end
    assert math.isclose(float(end_to_end["baseline_median_seconds"]), 11.0), end_to_end
    assert math.isclose(float(end_to_end["candidate_median_seconds"]), 6.0), end_to_end
    assert math.isclose(float(end_to_end["speedup"]), 11.0 / 6.0), end_to_end

    kernel = items[("axpy", "kernel")]
    assert kernel.get("status") == "ok", kernel
    assert math.isclose(float(kernel["speedup"]), 2.0), kernel
    assert_no_claim(items[("bad-output", "end-to-end")], "invalid-correctness")
    assert_no_claim(items[("short", "end-to-end")], "insufficient-samples")
    assert_no_claim(items[("bad-clock", "end-to-end")], "invalid-timing")

    malformed = subprocess.run(
        [sys.executable, str(script), str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert malformed.returncode != 0, malformed
    print("benchmark report verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
