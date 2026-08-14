#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/benchmark.py may change."
    exit 1
}

grep -Eq 'from[[:space:]]+onedal\.linear_model[[:space:]]+import[[:space:]]+LinearRegression' /app/benchmark.py || {
    echo "The repair must preserve the oneDAL LinearRegression estimator."
    exit 1
}

python /app/reproduce.py

python - <<'PY'
import json
from pathlib import Path

import numpy as np

from benchmark import benchmark_pipeline


class StepClock:
    def __init__(self, values):
        self.values = iter(values)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return next(self.values)


def run_case(seed, sample_count, feature_count, query_count, repeats):
    rng = np.random.default_rng(seed)
    samples = rng.normal(size=(sample_count, feature_count))
    coefficients = rng.normal(size=feature_count)
    targets = samples @ coefficients
    queries = rng.normal(size=(query_count, feature_count))
    expected = queries @ coefficients
    clock = StepClock((100.0, 102.5, 111.0))
    metrics = benchmark_pipeline(
        samples.tolist(),
        targets.tolist(),
        queries.tolist(),
        repeats=repeats,
        clock=clock,
    )
    assert clock.calls == 3, clock.calls
    assert metrics["conversion_seconds"] == 2.5, metrics
    assert metrics["compute_seconds"] == 8.5, metrics
    assert metrics["end_to_end_seconds"] == 11.0, metrics
    error = abs(metrics["prediction_sum"] - float(np.sum(expected)))
    assert error < 1.0e-8, error
    return error


cases = (
    (5732, 73, 4, 11, 1),
    (1018, 257, 9, 17, 2),
    (3648, 129, 6, 5, 4),
)
errors = [run_case(*case) for case in cases]
reward = {
    "reward": 1.0,
    "hidden_cases": len(cases),
    "max_prediction_sum_error": max(errors),
}
Path("/logs/verifier/reward.json").write_text(
    json.dumps(reward, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(reward, indent=2))
PY
