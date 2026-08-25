# oneDPL overloaded-comma iterator calibration: 2026-08-14

## Outcome

`onedpl-iterator-category-failure` is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms all repaired the pinned oneDPL source and passed the public transform plus hidden algorithm, numeric-scan, and memory cases at reward `1.0`. All three trials completed without exceptions.

The task remains valuable as live hosted-CPU regression coverage for a verified maintainer incident. It does not demonstrate a skill quality advantage, so it is classified `smoke` / `ceiling` and does not justify a three-attempt calibration.

## Matched results

| Arm | Reward | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 993,155 | $1.040202 | 4m 33s |
| Original skill (`476bfc8`) | 1.0000 | 690,813 | $0.924262 | 5m 46s |
| Current skill (`51759dc`) | 1.0000 | 947,688 | $1.058636 | 5m 25s |

Current-skill changes:

- Versus no skill: 4.6% fewer tokens, 1.8% higher cost, and 19.0% longer runtime at unchanged quality.
- Versus the original skill: 37.2% more tokens, 14.5% higher cost, and 6.1% shorter runtime at unchanged quality.

These efficiency differences are directional evidence from one attempt, not durable claims. Quality is the gate, and every arm reached the same full quality.

## Classification and next gate

Retain the task as a real-incident smoke/regression check. Do not add issue-specific comma-operator repair instructions to the skill: the model solves the failure from compiler evidence without them, and the current general skill did not reduce cost versus the original skill.

Future oneDPL skill-quality evidence should come from the existing `onedpl-missing-device-synchronization` headroom task or a harder independently sourced workflow with residual model headroom. Do not spend more attempts on this task unless the prompt, model, or skill changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `51759dca8bb0d09f62d73bbeaeec6f34165d04ae`.
- Comparison prefix: `onedpl-no-comma-calibration-20260813`.
- Raw comparison: `harbor-jobs/onedpl-no-comma-calibration-20260813-comparison.md`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onedpl-no-comma-calibration-20260813-noskill)
- [Original skill](http://127.0.0.1:8080/jobs/onedpl-no-comma-calibration-20260813-previous)
- [Current skill](http://127.0.0.1:8080/jobs/onedpl-no-comma-calibration-20260813-candidate)
