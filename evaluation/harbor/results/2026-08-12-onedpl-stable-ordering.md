# oneDPL stable-ordering live evaluation

Date: 2026-08-12

## Purpose

Add real hosted-CPU oneDPL coverage for an algorithm-contract bug: a key sort is correct, but downstream semantics also require original arrival order among equal keys. A parallel unstable sort cannot satisfy that requirement merely because its output is key-sorted.

## Runtime and source basis

- oneDPL source pinned to `7be7189277bf0d0992806edc080b153046e5c2ac`.
- oneDPL host `par` execution policy, linked against oneTBB.
- Generic hosted CPU; no device or performance claim.
- The current [oneAPI specification for oneDPL execution policies](https://uxlfoundation.github.io/oneAPI-spec/spec/elements/oneDPL/source/parallel_api/execution_policies.html) documents the standard-aligned host policies exercised by this task.

This is a constructed regression, not a maintainer incident.

## Acceptance evidence

- Unchanged reproducer: fails stable order with equal-key inversion `1:206` before `1:83`.
- Accepted repair: changes the algorithm contract from unstable sort to stable sort while retaining oneDPL `par` and the key-only comparator.
- Held-out verification: four distributions, including 1,021 events/13 keys, one-key all-equal input, and 509 events/37 keys.
- Harbor `0.20.0` oracle job: `harbor-jobs/onedpl-stable-oracle-20260812`
- Trials: 1 completed, 0 exceptions, reward `1.0`.

The verifier also checks key ordering, exact input permutation, and monotonic arrival order within every equal-key group.

## Interpretation and limit

The task provides live oneDPL host-policy correctness coverage on free runners. It does not test a historical project regression, device policies, or performance. A matched [three-arm calibration](2026-08-12-onedpl-stable-calibration.md) found that every arm passed, so this is retained as a smoke test rather than evidence of skill discrimination.
