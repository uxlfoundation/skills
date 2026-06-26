#!/usr/bin/env python3
"""Summarize benchmark CSV rows with columns: case,variant,seconds,correct."""

from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: summarize_runs.py results.csv", file=sys.stderr)
        return 2

    path = Path(argv[1])
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    correctness: dict[tuple[str, str], set[str]] = defaultdict(set)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"case", "variant", "seconds", "correct"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            print(f"missing columns: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
        for row in reader:
            key = (row["case"], row["variant"])
            groups[key].append(float(row["seconds"]))
            correctness[key].add(row["correct"].strip().lower())

    print("| Case | Variant | Runs | Median seconds | Correct |")
    print("| --- | --- | ---: | ---: | --- |")
    for (case, variant), values in sorted(groups.items()):
        status = ",".join(sorted(correctness[(case, variant)]))
        print(f"| {case} | {variant} | {len(values)} | {statistics.median(values):.6g} | {status} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
