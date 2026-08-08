#!/usr/bin/env python3
"""Compare reduction outputs. This starter uses an unsafe tolerance rule."""

import json
import math
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    data = json.load(source)

pairs = [
    (reference, candidate)
    for reference, candidate in zip(data["reference"], data["candidate"])
    if math.isfinite(reference) and math.isfinite(candidate)
]
errors = [abs(candidate - reference) for reference, candidate in pairs]
mismatches = sum(error > data["atol"] for error in errors)
worst_index = errors.index(max(errors)) if errors else None

print(
    json.dumps(
        {
            "schema_version": "1.0",
            "status": "pass" if mismatches == 0 else "fail",
            "sample_count": len(pairs),
            "mismatch_count": mismatches,
            "atol": data["atol"],
            "rtol": data["rtol"],
            "max_absolute_error": max(errors, default=0.0),
            "worst_index": worst_index,
        }
    )
)
