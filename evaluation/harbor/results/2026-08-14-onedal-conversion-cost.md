# oneDAL conversion-cost benchmark: 2026-08-14

## Outcome

`onedal-conversion-cost-benchmark` is a live generic-CPU benchmark-instrumentation task. A framework-style boundary supplies Python row lists, the application converts them to float64 NumPy arrays, and `onedal.linear_model.LinearRegression` performs repeated fit/predict work. The broken benchmark starts its clock after conversion and reports compute-only duration as end-to-end duration, hiding a real integration cost.

The repair measures three non-overlapping values: boundary conversion, oneDAL compute, and their end-to-end sum. It preserves the list boundary, data type, oneDAL estimator, repeat count, and prediction checksum. It neither adds a speed threshold nor claims that this runner represents target-device performance.

## Evaluation contract

The public run uses the real monotonic clock and verifies oneDAL prediction parity. Three hidden cases vary shape, seed, and repeat count while injecting a deterministic three-step clock. The deterministic path proves exact timing boundaries without making the evaluator depend on noisy wall-clock ratios.

| Gate | Result |
| --- | ---: |
| Untouched benchmark | Conversion reported as zero; reward 0 |
| Direct oracle | Public parity plus 3 hidden timing cases pass |
| Harbor oracle | 1.000; 1 trial; 0 exceptions; 23 s |
| Harbor empty baseline | 0.000; 1 trial; 0 exceptions; 20 s |
| Required hardware | Generic hosted CPU |

## Portfolio effect and next gate

The portfolio now has 36 of 49 tasks implemented, and oneDAL has five of six. All generic-CPU oneDAL tasks are implemented; its sole remaining slot intentionally requires a target GPU for an unavailable-device workflow.

The [matched calibration](2026-08-14-onedal-conversion-calibration.md) found a three-arm quality ceiling with higher current-skill token burn, so the task is classified `smoke` / `ceiling` and retained as benchmark-regression coverage.

Harbor jobs:

- [Oracle](http://127.0.0.1:8080/jobs/onedal-conversion-oracle-20260814-r1)
- [Empty baseline](http://127.0.0.1:8080/jobs/onedal-conversion-baseline-20260814-r1)
