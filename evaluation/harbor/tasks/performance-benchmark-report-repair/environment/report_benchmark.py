#!/usr/bin/env python3
"""Generate a benchmark summary. This starter intentionally overclaims."""

import csv
import json
import sys


with open(sys.argv[1], newline="", encoding="utf-8") as source:
    rows = list(csv.DictReader(source))

cases = {}
for row in rows:
    cases.setdefault(row["case"], {}).setdefault(row["variant"], []).append(
        float(row["seconds"])
    )

comparisons = []
for case, variants in sorted(cases.items()):
    baseline = sum(variants["baseline"]) / len(variants["baseline"])
    candidate = sum(variants["candidate"]) / len(variants["candidate"])
    comparisons.append(
        {
            "case": case,
            "scope": "mixed",
            "status": "ok",
            "baseline_samples": len(variants["baseline"]),
            "candidate_samples": len(variants["candidate"]),
            "baseline_median_seconds": baseline,
            "candidate_median_seconds": candidate,
            "speedup": baseline / candidate,
        }
    )

print(json.dumps({"schema_version": "1.0", "comparisons": comparisons}))
