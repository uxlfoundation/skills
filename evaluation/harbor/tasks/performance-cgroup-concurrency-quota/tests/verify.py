#!/usr/bin/env python3
"""Behavioral verifier for cgroup-aware oneTBB arena concurrency."""

from __future__ import annotations

import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


EXPECTED_KEYS = {"schedulable", "requested", "arena", "checksum"}
EXPECTED_CHECKSUM = sum((index % 97) + 1 for index in range(10_000))
EXPECTED_SCHEDULABLE = len(os.sched_getaffinity(0))


def run_probe(binary: Path, cpu_max: Path) -> dict[str, int]:
    result = subprocess.run(
        [str(binary), str(cpu_max)],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    parsed: dict[str, int] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        assert separator and key not in parsed, result.stdout
        parsed[key] = int(value)
    assert set(parsed) == EXPECTED_KEYS, parsed
    assert parsed["schedulable"] == EXPECTED_SCHEDULABLE, parsed
    assert parsed["checksum"] == EXPECTED_CHECKSUM, parsed
    return parsed


def expected_limit(schedulable: int, quota: int, period: int) -> int:
    return min(schedulable, max(1, math.ceil(quota / period)))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: verify.py PROBE")
    binary = Path(argv[1])

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        unconstrained = root / "unconstrained.max"
        unconstrained.write_text("max 100000\n", encoding="utf-8")
        baseline = run_probe(binary, unconstrained)
        schedulable = EXPECTED_SCHEDULABLE
        assert baseline["requested"] == schedulable, baseline
        assert baseline["arena"] == schedulable, baseline

        numeric_cases = [
            (100_000, 100_000),
            (150_000, 100_000),
            (300_000, 100_000),
            (999_999, 100_000),
        ]
        for index, (quota, period) in enumerate(numeric_cases):
            fixture = root / f"numeric-{index}.max"
            fixture.write_text(f"{quota} {period}\n", encoding="utf-8")
            observed = run_probe(binary, fixture)
            expected = expected_limit(schedulable, quota, period)
            assert observed["requested"] == expected, observed
            assert observed["arena"] == expected, observed

        malformed_values = [
            "garbage\n",
            "100000 0\n",
            "0 100000\n",
            "100000 100000 extra\n",
            "18446744073709551616 100000\n",
        ]
        for index, contents in enumerate(malformed_values):
            fixture = root / f"malformed-{index}.max"
            fixture.write_text(contents, encoding="utf-8")
            observed = run_probe(binary, fixture)
            assert observed["requested"] == schedulable, observed
            assert observed["arena"] == schedulable, observed

        missing = run_probe(binary, root / "missing.max")
        assert missing["requested"] == schedulable, missing
        assert missing["arena"] == schedulable, missing

        live_path = Path("/sys/fs/cgroup/cpu.max")
        quota_token, period_token = live_path.read_text(encoding="utf-8").split()
        assert quota_token != "max", "task container must have a numeric CPU quota"
        live = run_probe(binary, live_path)
        live_expected = expected_limit(schedulable, int(quota_token), int(period_token))
        assert live["requested"] == live_expected, live
        assert live["arena"] == live_expected, live

    print("cgroup concurrency verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
