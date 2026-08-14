# oneMath packed/band storage calibration: 2026-08-13

## Outcome

`onemath-packed-band-storage-fixtures` is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms each repaired the TPSV/TBSV storage regression and passed every public and hidden check at reward `1.0`, with no exceptions.

The task is reclassified from `discriminating` to `smoke`. It remains useful live maintainer-origin coverage for oneMath BLAS storage contracts, but it cannot demonstrate skill quality and does not warrant a three-attempt calibration without a material task, skill, or model change.

## Matched results

| Arm | Verified successes | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 354,499 | $0.604834 | 4m 11s |
| Original skill (`476bfc8`) | 1/1 | 433,532 | $0.646753 | 4m 25s |
| Current skill (`bad3cee`) | 1/1 | 820,443 | $0.976471 | 6m 18s |

Candidate changes:

- Versus no skill: 131.4% more tokens per verified success, 61.4% higher cost, and 50.6% longer runtime.
- Versus the original skill: 89.2% more tokens per verified success, 51.0% higher cost, and 42.6% longer runtime.

This one-attempt screen identifies a full-quality ceiling but is not a statistical efficiency estimate. It provides no evidence that the current skill reduces token burn on this incident.

## Repair audit

All three artifacts added generalized packed and band fixture logic and updated both affected call sites. The immutable dense generator and public reproducer retained their original checksums. The hidden verifier passed all 24 combinations of layout, triangle, transpose mode, and matrix size, checking complete arrays and padded band regions.

## Classification and next gate

Classify the task as `ceiling` and retain it as live smoke/regression coverage. The next oneMath skill-quality task should preserve residual model headroom through backend/dispatch integration or a multi-stage runtime diagnosis. Do not spend more attempts on this task unless the prompt, skill, or model changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `bad3cee682de55db7f9da21de649a80be5c4d626`.
- Comparison prefix: `onemath-storage-calibration-20260813`.
- Raw comparison: `harbor-jobs/onemath-storage-calibration-20260813-comparison.md`.
