# oneDPL overloaded-comma iterator incident: 2026-08-13

## Outcome

`onedpl-iterator-category-failure` is a live hosted-CPU source-repair task derived from [oneDPL issue #2342](https://github.com/uxlfoundation/oneDPL/issues/2342) and its accepted repair, [PR #2369](https://github.com/uxlfoundation/oneDPL/pull/2369). It replaces the compiler-specific reverse-iterator candidate that could not be reproduced authentically on the lightweight runner.

The task pins oneDPL commit `6e50ced8bd7120058fe0a743c3b826fc7c641af0`, immediately before the accepted repair. A conforming random-access iterator deletes its comma operator. The pre-fix library accidentally invokes that overload through comma-separated iterator increments in internal loops, so a valid parallel transform fails to compile. The accepted head `3beb90dba45d7433bda97d4f1046f0037e0a7907` protects the increment expressions and passes unchanged.

## Evaluation contract

The public reproducer exercises `oneapi::dpl::transform` with the host `par` policy and validates the output. Hidden cases extend the same iterator contract to transform scan and uninitialized copy, requiring a generalized library repair rather than a one-line special case. The verifier hashes the public reproducer and rejects consumer-side weakening.

| Gate | Result |
| --- | ---: |
| Direct pinned baseline | Compile failure at `algorithm_impl.h:276` |
| Direct accepted repair | Public and hidden programs pass |
| Harbor oracle | 1.000; 1 trial; 0 exceptions; 29 s |
| Harbor empty baseline | 0.000; 1 trial; 0 exceptions; 25 s |
| Required hardware | Generic hosted CPU |

## Portfolio effect and next gate

The portfolio now has 34 of 49 tasks implemented, and oneDPL has four of six. This task counts as real maintainer-incident reproduce/investigate/repair/verify coverage.

The [matched calibration](2026-08-14-onedpl-no-comma-calibration.md) found a three-arm quality ceiling, so the task is classified `smoke` / `ceiling` and retained as durable regression coverage.

Harbor jobs:

- [Oracle](http://127.0.0.1:8080/jobs/onedpl-no-comma-oracle-20260813-r1)
- [Empty baseline](http://127.0.0.1:8080/jobs/onedpl-no-comma-baseline-20260813-r1)
