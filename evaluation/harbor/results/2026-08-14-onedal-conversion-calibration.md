# oneDAL conversion-cost calibration: 2026-08-14

## Outcome

`onedal-conversion-cost-benchmark` is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms all repaired the timing boundaries and passed the live oneDAL parity check plus three deterministic hidden timing cases at reward `1.0`. All trials completed without exceptions.

The task remains useful as live generic-CPU coverage of conversion-aware benchmark reporting. It cannot demonstrate skill quality lift, so it is classified `smoke` / `ceiling`; no three-attempt calibration is warranted.

## Matched results

| Arm | Reward | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 92,499 | $0.123776 | 1m 49s |
| Original skill (`476bfc8`) | 1.0000 | 114,984 | $0.172651 | 2m 13s |
| Current skill (`64f3d49`) | 1.0000 | 132,561 | $0.195067 | 2m 04s |

Current-skill changes:

- Versus no skill: 43.3% more tokens, 57.6% higher cost, and 13.8% longer runtime at unchanged quality.
- Versus the original skill: 15.3% more tokens, 13.0% higher cost, and 6.8% shorter runtime at unchanged quality.

These efficiency differences are directional evidence from one attempt. They provide no reason to add task-specific conversion-timing instructions to the skill.

## Classification and next gate

Retain the task as deterministic benchmark-regression coverage. Use `onedal-sklearn-or-native-kmeans` and other headroom tasks for skill-quality claims, and real maintainer incidents for live repair evidence. Do not spend more attempts here unless the task, skill, or model changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `64f3d498c4b3dd02c7afaecb17df06f8d10d22ea`.
- Comparison prefix: `onedal-conversion-calibration-20260814`.
- Raw comparison: `harbor-jobs/onedal-conversion-calibration-20260814-comparison.md`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onedal-conversion-calibration-20260814-noskill)
- [Original skill](http://127.0.0.1:8080/jobs/onedal-conversion-calibration-20260814-previous)
- [Current skill](http://127.0.0.1:8080/jobs/onedal-conversion-calibration-20260814-candidate)
