# oneMath triangular packed/band storage incident: 2026-08-13

This wave implements `onemath-packed-band-storage-fixtures`, a hosted-CPU source-repair task derived from [oneMath PR #85](https://github.com/uxlfoundation/oneMath/pull/85). It replaces the unassigned `onemath-blas-leading-dimension` placeholder, keeping the portfolio fixed at 49 tasks while raising implemented coverage to 32.

## Reproduction basis

The accepted upstream repair found that the TPSV and TBSV unit tests reused a dense triangular matrix generator. TPSV requires compact packed storage, while TBSV requires the selected triangle to be placed in specific rows of a leading-dimension-padded band array. The dense fixture therefore did not represent the storage contract exercised by either routine.

The task pins the affected control flow from pre-fix commit `c80fe1df72ebe63e570806e3323b6a6265c96b6c` and the repair from PR head `18d13bbd2855e47fffed09f040b053dc95bbf237`. Because the historical test tree depends on an obsolete SYCL toolchain and backend stack, the evaluator minimizes the fixture logic into standard C++ while preserving the dense generator, the erroneous TPSV/TBSV call sites, and the accepted conversion algorithms. The immutable support and public reproducer are protected by SHA-256 checksums.

The packaged unchanged baseline fails both public signals:

| Contract | Pre-fix result | Required result |
| --- | --- | --- |
| Five-by-five TPSV fixture | 25 dense elements | 15 packed elements |
| Seven-by-seven TBSV fixture | Diagonal in dense positions | Diagonal in band row `k` |

## Oracle and hidden-case gate

The oracle applies the accepted repair pattern: add dedicated packed and band generators, then select them at both call sites. The hidden verifier independently checks 24 configurations spanning:

- Column-major and row-major layout.
- Upper and lower triangles.
- Non-transposed and transposed fixture generation.
- Matrix sizes 1, 4, and 9.
- Zero and nonzero band widths with padded leading dimensions.

Every configuration checks the complete packed vector and band array, including zero padding. The unchanged image scores `0`; the oracle scores `1` across the public and held-out cases.

Harbor 0.20.0 reproduced that boundary with zero exceptions:

| Arm | Job | Reward | Runtime |
| --- | --- | ---: | ---: |
| Accepted repair | `onemath-storage-oracle-20260813-r1` | 1.000 | 27 s |
| Unchanged source | `onemath-storage-baseline-20260813-r1` | 0.000 | 19 s |

## Scope and initial decision

This is live reproduce/investigate/repair/verify coverage for a real oneMath maintainer repair on a generic hosted CPU. It tests BLAS storage-contract and known-answer fixture reasoning; it does not execute a SYCL backend, qualify target hardware, or make a performance claim. The task enters the portfolio as `discriminating` / `uncalibrated` pending the matched skill comparison.
