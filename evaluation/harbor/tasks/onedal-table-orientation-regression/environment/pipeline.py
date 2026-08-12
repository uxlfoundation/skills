"""Train a oneDAL linear model from a column-oriented ingestion boundary."""

from __future__ import annotations

import numpy as np
from onedal.linear_model import LinearRegression


def train_and_predict(
    feature_columns: list[list[float]],
    targets: list[float],
    query_rows: list[list[float]],
) -> np.ndarray:
    """Fit from feature columns and predict for conventional sample rows."""
    training_table = np.asarray(feature_columns, dtype=np.float64)
    target_array = np.asarray(targets, dtype=np.float64)
    query_table = np.asarray(query_rows, dtype=np.float64)

    model = LinearRegression(fit_intercept=False)
    model.fit(training_table, target_array)
    return np.asarray(model.predict(query_table)).reshape(-1)
