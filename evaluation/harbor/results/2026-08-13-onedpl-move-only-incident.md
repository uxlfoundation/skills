# oneDPL move-only numeric accumulator incident: 2026-08-13

This wave implements `onedpl-move-only-numeric-accumulator`, a hosted-CPU source-repair task derived from [oneDPL issue #1955](https://github.com/uxlfoundation/oneDPL/issues/1955) and its accepted repair in [PR #2355](https://github.com/uxlfoundation/oneDPL/pull/2355). It replaces the unassigned `onedpl-host-backend-configuration` placeholder, keeping the portfolio fixed at 49 tasks while raising implemented coverage to 31.

## Reproduction gate

The task vendors the oneDPL headers at pre-fix commit `6e50ced8bd7120058fe0a743c3b826fc7c641af0`. The public reproducer passes a movable but non-copyable accumulator to `std::transform_reduce` with oneDPL's `par` and `par_unseq` host policies. The unchanged source fails to compile because the numeric dispatch path copies the accumulator while forwarding it between layers. The failure was reproduced first from the upstream checkout and then from the packaged task image.

The source archive is immutable during a trial, except for agent repairs inside `/app/oneDPL`. The public reproducer and its runner are protected by SHA-256 checksums. Debian Bookworm, GCC 12, and the distribution oneTBB package provide a generic hosted-CPU environment; the task makes no GPU or hardware-performance claim.

## Repair and hidden-case gate

The oracle overlays the complete `include` tree from accepted PR head `f63abeea3ee842ebedcba4b6652afdf105c48656`. That repair moves the accumulator through the public and internal numeric layers and updates host-backend storage and combination paths so they do not require a copy constructor.

The independent verifier covers more than the public failure:

| Case | Policy or iterator | Expected result | Oracle |
| --- | --- | ---: | ---: |
| Unary `transform_reduce` | `par` | 8,390,656 | Pass |
| Unary `transform_reduce` | `par_unseq` | 8,390,656 | Pass |
| `reduce` | `par` and `par_unseq` | 778,182 | Pass |
| Binary `transform_reduce` | `par` | 8,019 | Pass |
| Unary `transform_reduce` | forward iterator | -995,115 | Pass |
| Empty range | `par` | 1,234,567 identity | Pass |

The hidden checks retain deleted copy construction and copy assignment, use different data shapes, and exercise both random-access and forward iterators. They reject a consumer-side workaround or a repair specialized only to the public type.

## Harbor discrimination

Harbor 0.20.0 completed both evaluator-control trials with zero exceptions:

| Arm | Job | Reward | Runtime |
| --- | --- | ---: | ---: |
| Exact upstream repair | `onedpl-move-only-oracle-20260813-r1` | 1.000 | 40 s |
| Unchanged pre-fix source | `onedpl-move-only-baseline-20260813-r1` | 0.000 | 23 s |

This establishes live reproduce/investigate/repair/verify coverage for a real maintainer incident on hardware available to ordinary hosted runners. The subsequent [matched calibration](2026-08-13-onedpl-move-only-calibration.md) found a quality ceiling, so the task's final classification is `smoke` / `ceiling`.
