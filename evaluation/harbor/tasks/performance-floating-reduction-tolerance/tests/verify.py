#!/usr/bin/env python3
"""Behavioral verifier for floating-point reduction comparison."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


def run_comparison(script: Path, data, *, expect_success=True):
    with tempfile.TemporaryDirectory() as directory:
        input_path = Path(directory) / "input.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(script), str(input_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    if expect_success:
        assert result.returncode == 0, result.stderr
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"stdout is not one JSON document: {result.stdout!r}") from exc
    assert result.returncode != 0, result.stdout
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: verify.py SCRIPT")
    script = Path(argv[1])

    relative = run_comparison(
        script,
        {
            "reference": [1_000_000.0, -2_000_000.0, 3.0],
            "candidate": [1_000_000.5, -2_000_001.5, 3.0000004],
            "atol": 0.000001,
            "rtol": 0.000001,
        },
    )
    assert relative["schema_version"] == "1.0", relative
    assert relative["status"] == "pass", relative
    assert relative["sample_count"] == 3, relative
    assert relative["mismatch_count"] == 0, relative
    assert relative["atol"] == 0.000001 and relative["rtol"] == 0.000001, relative
    assert math.isclose(relative["max_absolute_error"], 1.5), relative
    assert relative["worst_index"] == 1, relative

    near_zero = run_comparison(
        script,
        {
            "reference": [0.0, 1000.0, -5.0],
            "candidate": [0.00001, 1000.0005, -5.01],
            "atol": 0.000001,
            "rtol": 0.000001,
        },
    )
    assert near_zero["status"] == "fail", near_zero
    assert near_zero["sample_count"] == 3, near_zero
    assert near_zero["mismatch_count"] == 2, near_zero
    assert near_zero["worst_index"] == 2, near_zero
    assert math.isclose(near_zero["max_absolute_error"], 0.01), near_zero

    boundary = run_comparison(
        script,
        {
            "reference": [0.0, 10.0],
            "candidate": [0.25, 10.75],
            "atol": 0.25,
            "rtol": 0.05,
        },
    )
    assert boundary["status"] == "pass" and boundary["mismatch_count"] == 0, boundary

    malformed = [
        {"reference": [1.0], "candidate": [], "atol": 0.0, "rtol": 0.0},
        {"reference": [], "candidate": [], "atol": 0.0, "rtol": 0.0},
        {"reference": [1.0, float("nan")], "candidate": [1.0, 2.0], "atol": 0.0, "rtol": 0.0},
        {"reference": [1.0], "candidate": [1.0], "atol": -1.0, "rtol": 0.0},
        {"reference": [True], "candidate": [1.0], "atol": 0.0, "rtol": 0.0},
        {"reference": [1.0], "candidate": [1.0], "atol": 0.0, "rtol": 0.0, "extra": 1},
    ]
    for data in malformed:
        run_comparison(script, data, expect_success=False)

    print("floating reduction verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
