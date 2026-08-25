"""Public reproducer for the oneDAL table-orientation quality regression."""

from __future__ import annotations

import numpy as np

from pipeline import train_and_predict


def main() -> int:
    rng = np.random.default_rng(5732)
    feature_count = 6
    sample_rows = rng.normal(size=(feature_count, feature_count))
    coefficients = np.asarray([1.5, -2.0, 0.75, 3.0, -1.25, 2.5])
    targets = sample_rows @ coefficients
    query_rows = rng.normal(size=(5, feature_count))
    expected = query_rows @ coefficients

    predicted = train_and_predict(
        sample_rows.T.tolist(),
        targets.tolist(),
        query_rows.tolist(),
    )
    rmse = float(np.sqrt(np.mean((predicted - expected) ** 2)))
    print(f"backend=onedal.linear_model.LinearRegression public_rmse={rmse:.12g}")
    if predicted.shape != expected.shape or not np.isfinite(predicted).all():
        return 2
    return 0 if rmse < 1.0e-8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
