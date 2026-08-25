Repair the oneDAL benchmark instrumentation in `/app/benchmark.py`.

The application boundary supplies Python row lists. The benchmark converts them to NumPy arrays, then fits and predicts with `onedal.linear_model.LinearRegression`. It currently starts timing after conversion and reports compute-only time as end-to-end time, hiding the framework-to-oneDAL conversion cost.

Run `/app/reproduce.py` before and after your change. Preserve the list input boundary, float64 conversion, oneDAL estimator, fit/predict work, repeat count, result checksum, and injectable `clock` argument. Report distinct non-overlapping conversion and compute durations plus their end-to-end duration. Do not add sleeps, synthetic timing values, a different estimator, or a speed threshold. Briefly explain the original measurement error, the corrected timing boundaries, and verification.
