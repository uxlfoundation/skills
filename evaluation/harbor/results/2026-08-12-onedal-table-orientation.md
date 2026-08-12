# oneDAL table-orientation live evaluation

Date: 2026-08-12

## Purpose

Add a real oneDAL CPU task for an integration bug that can silently damage model quality: an ingestion boundary supplies feature columns, while oneDAL expects observations in rows and features in columns. A square public fixture conceals the shape mismatch, so success also requires generalizing to held-out rectangular tables.

## Runtime and source basis

- Runtime: `scikit-learn-intelex==2026.1.0`, which supplies the `onedal` Python backend used by `onedal.linear_model.LinearRegression`.
- Python image: pinned `python:3.12-slim-bookworm` digest.
- Hardware: generic hosted CPU; no GPU or target-specific performance claim.
- oneDAL's [mathematical notation](https://uxlfoundation.github.io/oneDAL/onedal/notations.html) defines an `n × p` data set as rows of observations and columns of features.

This is a constructed regression, not a maintainer incident. It receives live reproduce/investigate/repair/verify credit, but not real-incident credit.

## Acceptance evidence

- Unchanged public reproducer: RMSE `7.48477544943`, nonzero exit.
- Accepted repair public RMSE: `4.09068600017e-15`.
- Hidden rectangular case (`13 × 4`) RMSE: `1.592675364431656e-15`.
- Hidden wide-feature case (`7 × 5`) RMSE: `5.768888059150692e-16`.
- Harbor `0.20.0` oracle job: `harbor-jobs/onedal-table-oracle-20260812`
- Trials: 1 completed, 0 exceptions, reward `1.0`.

The verifier preserves the real oneDAL estimator, prevents modification of the public reproducer, checks finite prediction shape, and requires numerical parity below `1e-8` on all three cases.

## Interpretation and limit

The task proves useful hosted-CPU coverage of table semantics and analytics parity. It does not test a project release regression, GPU behavior, or performance.

The subsequent [three-arm calibration](2026-08-12-onedal-table-calibration.md) found a one-attempt ceiling: every arm earned `1.0`. The candidate used 111,033 tokens, 17.8% more than the previous skill and 48.5% more than no skill. The task is therefore retained as live smoke coverage, not as evidence of skill benefit, and its task-specific skill wording was not retained.
