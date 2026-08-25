"""Public conversion-cost benchmark and correctness check."""

from __future__ import annotations

import json

import numpy as np

from benchmark import benchmark_pipeline


def main() -> int:
    rng = np.random.default_rng(3648)
    sample_count, feature_count, query_count = 256, 7, 19
    samples = rng.normal(size=(sample_count, feature_count))
    coefficients = rng.normal(size=feature_count)
    targets = samples @ coefficients
    queries = rng.normal(size=(query_count, feature_count))
    expected = queries @ coefficients

    metrics = benchmark_pipeline(
        samples.tolist(), targets.tolist(), queries.tolist(), repeats=3
    )
    expected_sum = float(np.sum(expected))
    error = abs(metrics["prediction_sum"] - expected_sum)
    print(json.dumps({**metrics, "prediction_sum_error": error}, indent=2))
    if error >= 1.0e-8:
        return 1
    if metrics["conversion_seconds"] <= 0.0:
        return 1
    if metrics["compute_seconds"] <= 0.0:
        return 1
    if abs(
        metrics["end_to_end_seconds"]
        - metrics["conversion_seconds"]
        - metrics["compute_seconds"]
    ) > 1.0e-9:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
