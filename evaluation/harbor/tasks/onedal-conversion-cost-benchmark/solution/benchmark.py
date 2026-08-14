"""Conversion-aware oneDAL benchmark with a framework-style list boundary."""

from __future__ import annotations

import time
from collections.abc import Callable

import numpy as np
from onedal.linear_model import LinearRegression


def benchmark_pipeline(
    feature_rows: list[list[float]],
    targets: list[float],
    query_rows: list[list[float]],
    repeats: int,
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, float]:
    """Measure conversion and oneDAL fit/predict work for one application batch."""
    if repeats <= 0:
        raise ValueError("repeats must be positive")

    overall_started = clock()
    feature_array = np.asarray(feature_rows, dtype=np.float64)
    target_array = np.asarray(targets, dtype=np.float64)
    query_array = np.asarray(query_rows, dtype=np.float64)
    conversion_finished = clock()

    prediction = None
    for _ in range(repeats):
        model = LinearRegression(fit_intercept=False)
        model.fit(feature_array, target_array)
        prediction = np.asarray(model.predict(query_array)).reshape(-1)
    compute_finished = clock()
    assert prediction is not None

    conversion_seconds = conversion_finished - overall_started
    compute_seconds = compute_finished - conversion_finished
    return {
        "conversion_seconds": conversion_seconds,
        "compute_seconds": compute_seconds,
        "end_to_end_seconds": compute_finished - overall_started,
        "prediction_sum": float(np.sum(prediction)),
    }
