# oneDNN reorder calibration: 2026-08-13

## Outcome

`onednn-extra-reorder-regression` is a quality ceiling under the current model. All three arms independently moved the transformed constant-weight memory outside the inference loop, executed one reorder and the requested number of real oneDNN convolutions, and passed all numerical checks at reward `1.0` with no exceptions.

The task is reclassified from `discriminating` to `smoke`. It remains useful live regression coverage for framework/oneDNN layout boundaries, but it cannot demonstrate skill quality and does not warrant a three-attempt calibration.

## Matched results

| Arm | Verified successes | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 96,852 | $0.132733 | 2m 23s |
| Original skill (`476bfc8`) | 1/1 | 121,772 | $0.246221 | 2m 53s |
| Current skill (`647cf32`) | 1/1 | 117,681 | $0.209083 | 2m 41s |

Candidate changes:

- Versus no skill: 21.5% more tokens per verified success, 57.5% higher cost, and 12.6% longer runtime.
- Versus the original skill: 3.4% fewer tokens per verified success, 15.1% lower cost, and 6.9% shorter runtime.

This one-attempt screen identifies a full-quality ceiling but is not a statistical efficiency estimate. It provides no evidence that the current skill reduces token burn relative to no skill.

## Repair audit

All three artifacts retained the framework-owned plain `oihw` weights, the oneDNN-selected optimized descriptor, and the actual convolution. Each allocated the selected weight memory once, executed the reorder once, waited for completion, and reused the transformed memory across the inference loop. The hidden verifier confirmed one reorder and two to five convolutions over three different channel/shape/seed cases.

## Classification and next gate

Classify the task as `ceiling` and retain it as live smoke/regression coverage. Future oneDNN skill-quality claims should rely on `onednn-framework-blocked-layout` or a new harder task with genuine model headroom. Do not spend more attempts on this task unless the prompt or skill changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `647cf32d84b93a4517c7914557ea29ee4249a087`.
- Comparison prefix: `onednn-reorder-calibration-20260813`.
- Raw comparison: `harbor-jobs/onednn-reorder-calibration-20260813-comparison.md`.
