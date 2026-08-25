# oneDAL ExtraTrees calibration: 2026-08-13

## Outcome

The maintainer-incident `onedal-extra-trees-random-split` task is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms all found the accepted two-line source repair and passed the four-case hidden verifier at reward `1.0` with no exceptions. All three submitted artifacts have the same SHA-256 digest.

The task remains valuable as live, hosted-CPU coverage of a real oneDAL quality regression, including reproduce, investigate, repair, and verify stages. It cannot demonstrate skill quality lift with this model, so it is classified `smoke` / `ceiling`; the one-attempt screen does not justify three-attempt calibration.

## Matched results

| Arm | Reward | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 2,282,761 | $1.664014 | 13m 12s |
| Original skill (`476bfc8`) | 1.0000 | 2,357,150 | $1.760291 | 13m 14s |
| Current skill (`205b090`) | 1.0000 | 2,123,727 | $1.622561 | 13m 18s |

Current-skill changes:

- Versus no skill: 7.0% fewer tokens per verified success, 2.5% lower cost, and 0.8% longer runtime.
- Versus the original skill: 9.9% fewer tokens per verified success, 7.8% lower cost, and 0.5% longer runtime.

The efficiency result is directional evidence from one attempt, not a statistically durable claim. Quality remains the gate, and all arms reached the same full quality.

## Behavior audit

Every arm reproduced the high-MSE, low-leaf failure, traced it to unweighted combination plus double normalization of child variances, applied the accepted repair, and verified unweighted and weighted behavior. The three collected source artifacts share digest `6c0aa2f97f8b7ec33621f8bc4b841b1d175158f0e951302e5c138b7b601865a7`.

The current skill supplied sensible validation context but did not contain incident-specific repair knowledge. This is consistent with the hardware-agnostic design: the task tests whether an agent can use oneDAL workflow guidance during real CPU triage, while oneDAL itself owns target-specific optimization.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `205b090cb360ad06ac0ffe99a692c0077b2f20a4`.
- Harbor: `0.20.0`; environment: hosted CPU, Debian Bookworm, GCC 12, OpenBLAS, and oneTBB.
- Comparison prefix: `onedal-extra-trees-calibration-20260813`.
- Raw comparison: `harbor-jobs/onedal-extra-trees-calibration-20260813-comparison.md`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onedal-extra-trees-calibration-20260813-noskill)
- [Original skill](http://127.0.0.1:8080/jobs/onedal-extra-trees-calibration-20260813-previous)
- [Current skill](http://127.0.0.1:8080/jobs/onedal-extra-trees-calibration-20260813-candidate)
