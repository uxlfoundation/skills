# oneCCL API-selection calibration: 2026-08-13

## Outcome

The current `uxl-oneccl` skill produced the strongest answers on the hardware-independent `oneccl-cpp-or-nccl-like-api` review task. Across three matched attempts, its mean reward was `0.6611`, versus `0.5833` for the original skill and `0.5278` without a skill. All nine trials completed without errors.

This is a quality improvement with residual headroom, not a verified-success claim. No arm reached the `1.0` quality gate. Even so, the current skill used 19.4% fewer total tokens than no skill and 20.5% fewer than the original skill while producing higher-quality answers.

## Matched results

| Arm | Mean reward | Total token burn | Cost | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 0.5278 | 512,968 | $1.014548 | 3m 21s |
| Original skill (`476bfc8`) | 0.5833 | 520,249 | $1.057966 | 4m 11s |
| Current skill (`8cf9596`) | 0.6611 | 413,421 | $0.971887 | 3m 34s |

Current-skill changes:

- Versus no skill: +0.1333 mean reward, 19.4% fewer tokens, 4.2% lower cost, and 6.5% longer runtime.
- Versus the original skill: +0.0778 mean reward, 20.5% fewer tokens, 8.1% lower cost, and 14.7% shorter runtime.

The current skill improved the `decision` group from `0.5000` to `0.6667` versus the original skill and the `correctness_and_rollout` group from `0.3333` to `0.4000`. Both skill arms averaged `0.9167` for support evidence, compared with `0.6667` without a skill. All arms received full credit for answer presence and avoiding unsupported compatibility claims.

## Development screen

The initial one-attempt screen pointed in the same direction: current skill `0.7167`, versus `0.4833` for both controls. The confirmation above is the calibration evidence because it repeats each arm three times and preserves the directional advantage.

## Classification and next gate

Classify `oneccl-cpp-or-nccl-like-api` as `discriminating` / `headroom`. It provides portable evidence that the skill helps an agent choose and validate oneCCL API boundaries without claiming that free runners reproduce device-specific collective failures.

Do not promote the task to verified-success evidence: the strongest remaining gap is correctness and rollout completeness. Use the failed rubric clauses to tighten the general oneCCL guidance, then rerun a development screen after a material skill change. Reserve five-attempt promotion evidence until the improvement also appears on an independently phrased oneCCL task.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 3; concurrency: 3.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `8cf9596641e90f649df8746078cd188cce0e79cc`.
- Confirmation prefix: `oneccl-api-confirmation-20260813`.
- Raw comparison: `harbor-jobs/oneccl-api-confirmation-20260813-comparison.md`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/oneccl-api-confirmation-20260813-noskill)
- [Original skill](http://127.0.0.1:8080/jobs/oneccl-api-confirmation-20260813-previous)
- [Current skill](http://127.0.0.1:8080/jobs/oneccl-api-confirmation-20260813-candidate)
