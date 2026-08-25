# oneDPL move-only numeric calibration: 2026-08-13

## Outcome

`onedpl-move-only-numeric-accumulator` is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms each repaired the move-only accumulator regression and passed every public and hidden check at reward `1.0`, with no exceptions.

The task is reclassified from `discriminating` to `smoke`. It remains valuable real maintainer-incident coverage for oneDPL's parallel numeric backends, but it cannot demonstrate skill quality and does not warrant a three-attempt calibration without a material task, skill, or model change.

## Matched results

| Arm | Verified successes | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 784,119 | $0.883338 | 8m 09s |
| Original skill (`476bfc8`) | 1/1 | 1,275,672 | $1.293474 | 5m 28s |
| Current skill (`c9ed4fc`) | 1/1 | 2,328,801 | $2.055758 | 7m 27s |

Candidate changes:

- Versus no skill: 197.0% more tokens per verified success, 132.7% higher cost, and 8.6% shorter runtime.
- Versus the original skill: 82.6% more tokens per verified success, 58.9% higher cost, and 36.3% longer runtime.

This one-attempt screen identifies a full-quality ceiling but is not a statistical efficiency estimate. It provides no evidence that the current skill reduces token burn on this incident.

## Repair audit

All three artifacts made generalized source-level changes rather than weakening the non-copyable consumer type. The verifier retained deleted copy operations and covered `reduce`, unary and binary `transform_reduce`, `par`, `par_unseq`, random-access and forward iterators, and an empty range. Every arm passed the same immutable public-reproducer checksum and hidden tests.

## Classification and next gate

Classify the task as `ceiling` and retain it as live smoke/regression coverage. The next oneDPL task should target residual model headroom, likely a harder iterator/device-result triage incident, rather than repeating this repair. Do not spend more attempts on this task unless the prompt, skill, or model changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `c9ed4fcf7b684009f3869ebdbf25247221715e4f`.
- Comparison prefix: `onedpl-move-only-calibration-20260813`.
- Raw comparison: `harbor-jobs/onedpl-move-only-calibration-20260813-comparison.md`.
