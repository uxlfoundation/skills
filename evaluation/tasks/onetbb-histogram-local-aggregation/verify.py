#!/usr/bin/env python3
"""Verify the histogram task solution."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path


def load_solution(workspace: Path):
    path = workspace / "histogram.py"
    if not path.exists():
        raise AssertionError("missing histogram.py")
    spec = importlib.util.spec_from_file_location("candidate_histogram", path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not import histogram.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference(values: list[int], bins: int) -> list[int]:
    counts = [0] * bins
    for value in values:
        counts[value % bins] += 1
    return counts


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify.py <workspace>", file=sys.stderr)
        return 2
    workspace = Path(argv[1]).resolve()
    module = load_solution(workspace)
    if not hasattr(module, "histogram"):
        raise AssertionError("histogram.py must define histogram(values, bins=16, workers=4)")

    source = inspect.getsource(module.histogram)
    if "local" not in source.casefold():
        raise AssertionError("solution should use partition-local aggregation")
    if "counts[bucket] = current + 1" in source:
        raise AssertionError("solution still uses shared read-modify-write update")

    datasets = [
        [],
        list(range(128)),
        [(index * 17 + 3) % 257 for index in range(1000)],
        [5] * 257 + [7] * 129 + [31, 47, 63, 79],
    ]
    for bins in (1, 2, 8, 16, 31):
        for workers in (1, 2, 4, 7):
            for values in datasets:
                actual = module.histogram(values, bins=bins, workers=workers)
                expected = reference(values, bins)
                if actual != expected:
                    raise AssertionError(
                        f"wrong result for bins={bins} workers={workers}: {actual} != {expected}"
                    )

    print("histogram verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
