#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/pipeline.py may change."
    exit 1
}

grep -Eq 'from[[:space:]]+onedal\.linear_model[[:space:]]+import[[:space:]]+LinearRegression' /app/pipeline.py || {
    echo "The repair must preserve the oneDAL LinearRegression estimator."
    exit 1
}

python /app/reproduce.py

python - <<'PY'
import json
from pathlib import Path

import numpy as np

from pipeline import train_and_predict


def run_case(seed: int, sample_count: int, feature_count: int, query_count: int) -> float:
    rng = np.random.default_rng(seed)
    sample_rows = rng.normal(size=(sample_count, feature_count))
    coefficients = rng.normal(size=feature_count)
    targets = sample_rows @ coefficients
    query_rows = rng.normal(size=(query_count, feature_count))
    expected = query_rows @ coefficients
    predicted = train_and_predict(
        sample_rows.T.tolist(),
        targets.tolist(),
        query_rows.tolist(),
    )
    assert predicted.shape == expected.shape, (predicted.shape, expected.shape)
    assert np.isfinite(predicted).all()
    rmse = float(np.sqrt(np.mean((predicted - expected) ** 2)))
    assert rmse < 1.0e-8, rmse
    return rmse


scores = {
    "public_square_rmse": run_case(5732, 6, 6, 5),
    "hidden_rectangular_rmse": run_case(1018, 13, 4, 7),
    "hidden_wide_rmse": run_case(1002, 7, 5, 3),
}
Path("/logs/verifier/reward.json").write_text(
    json.dumps({"reward": 1.0, **scores}, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(scores, indent=2))
PY
