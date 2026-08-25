# oneDAL ExtraTrees random-split incident: 2026-08-13

This wave implements `onedal-extra-trees-random-split`, a hosted-CPU source-level task derived from [oneDAL issue #3648](https://github.com/uxlfoundation/oneDAL/issues/3648) and its accepted repair in [PR #3649](https://github.com/uxlfoundation/oneDAL/pull/3649). It replaces the unassigned `onedal-train-infer-metric-parity` placeholder, keeping the portfolio fixed at 49 tasks while raising implemented coverage to 30.

## Reproduction gate

The issue's Python scenario was first reproduced against `scikit-learn-intelex==2026.1.0` in three independent runs. All three were identical: oneDAL ExtraTrees produced MSE `19188.724281154187` and only 355 unique predictions for 10,000 training rows, while oneDAL RandomForest and sklearn ExtraTrees each produced MSE `0` and 10,000 unique predictions.

The Harbor task vendors oneDAL release `2026.1.0` source commit `4681fc938a4b8062d286931589bdadc3398a12c0`. A deterministic C++ reproducer isolates the same random-split forest path. The pinned pre-fix source failed all three initial shapes:

| Shape | Pre-fix MSE | Unique predictions |
| --- | ---: | ---: |
| 10,000 x 10 | 4,758.76 | 12 / 10,000 |
| 4,096 x 7 | 1,440.81 | 14 / 4,096 |
| 2,048 x 4 | 263.707 | 13 / 2,048 |

## Environment normalization

The task uses Debian Bookworm, GCC 12, OpenBLAS, oneTBB, and generic SSE2 dispatch. Two GCC `__assume__` statements introduced for newer GCC releases do not compile under GCC 12; the Docker build removes only those compiler hints before establishing the immutable task baseline. That normalization is distinct from the ExtraTrees repair and leaves the reported impurity bug intact.

The complete upstream source archive is vendored, and neither image build nor trial execution downloads oneDAL source at runtime. The image prebuilds only the `dtrees/forest` dependency closure; a trial recompiles affected objects only after an agent edit. The local Harbor installation's offline mode requires an unconfigured egress sidecar, so the task declares the standard public mode for portability even though its task workflow performs no network calls.

## Oracle and hidden-case gate

The oracle installs the exact PR #3649 source repair. The independent verifier preserves the random splitter and `bootstrap=false`, rebuilds the library, and runs three unweighted cases plus a held-out weighted case:

| Case | Oracle MSE | Unique predictions | Result |
| --- | ---: | ---: | --- |
| 10,000 x 10, public seed | 0 | 9,997 / 10,000 | Pass |
| 4,096 x 7, hidden seed | 0 | 4,095 / 4,096 | Pass |
| 2,048 x 4, hidden seed | 0 | 2,048 / 2,048 | Pass |
| 3,072 x 6, hidden weighted | 0 | 3,072 / 3,072 | Pass |

The packaged oracle received reward `1.0`. A Harbor 0.20.0 native run completed one trial with zero exceptions and reward `1.000` in 7 minutes 18 seconds (`onedal-extra-trees-oracle-20260813-r6`). The matching unchanged baseline completed with zero exceptions and reward `0.000` (`onedal-extra-trees-baseline-20260813-r1`), confirming that the task discriminates the broken implementation from the upstream repair. The small unique-value collisions in two cases result from the diagnostic's six-decimal quantization; exact MSE is the primary correctness gate and the verifier permits at most 1% quantized collisions.

## Initial portfolio decision

The task entered the portfolio as a `discriminating` candidate with calibration state `uncalibrated`. It is oneDAL's first task that meets the full real end-to-end standard: live reproduction, reproduce/investigate/repair/verify workflow, and maintainer-incident origin. The subsequent matched screen is recorded in [oneDAL ExtraTrees calibration](2026-08-13-onedal-extra-trees-calibration.md); because all three arms solved it, the final classification is `smoke` / `ceiling`.
