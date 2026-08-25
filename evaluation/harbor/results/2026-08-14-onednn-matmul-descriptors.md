# oneDNN batched-matmul memory descriptors: 2026-08-14

## Outcome

`onednn-matmul-memory-descriptors` is a live generic-CPU task for a common framework integration boundary: a weights buffer is physically packed as `[batch][n][k]` but consumed by oneDNN matmul as the logical tensor `[batch][k][n]`. Declaring it with the default contiguous `abc` descriptor is valid API usage and executes without an exception, but interprets the bytes in the wrong order and produces incorrect numerics.

The repair must describe the existing storage with logical strides `{n*k, 1, k}` or an equivalent oneDNN format tag. It may not transpose, repack, copy, or manually recompute the weights or result. This keeps the task focused on API and memory-descriptor correctness rather than hardware-specific optimization.

## Evaluation contract

The public case uses asymmetric dimensions and compares every result element with an independent scalar reference. Four hidden cases vary batch, M, K, N, and seed. The source must retain oneDNN matmul descriptor creation, application-owned memory handles, primitive execution, and stream completion; the public reproducer is hashed.

| Gate | Result |
| --- | ---: |
| Untouched descriptor | Maximum absolute error about 1.0; reward 0 |
| Direct oracle | Public error `5.56e-08`; 4 hidden cases pass |
| Harbor oracle | 1.000; 1 trial; 0 exceptions; 23 s |
| Harbor empty baseline | 0.000; 1 trial; 0 exceptions; 19 s |
| Required hardware | Generic hosted CPU |

## Portfolio effect and next gate

The portfolio now has 35 of 49 tasks implemented, and oneDNN has five of six. All generic-CPU oneDNN tasks are implemented; the sole remaining oneDNN slot intentionally requires a target device for an unsupported-backend workflow.

The [matched calibration](2026-08-14-onednn-matmul-calibration.md) found a three-arm quality ceiling, so the task is classified `smoke` / `ceiling` and retained strictly as regression coverage. Harder answer-quality or real-incident tasks remain the basis for skill-lift claims.

Harbor jobs:

- [Oracle](http://127.0.0.1:8080/jobs/onednn-matmul-oracle-20260814-r1)
- [Empty baseline](http://127.0.0.1:8080/jobs/onednn-matmul-baseline-20260814-r1)
