# oneDNN matmul descriptor calibration: 2026-08-14

## Outcome

`onednn-matmul-memory-descriptors` is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms all corrected the weights memory descriptor and passed the public plus four hidden numeric-parity cases at reward `1.0`. All three trials completed without exceptions and produced the oracle result accuracy.

The task remains useful as live generic-CPU coverage of oneDNN memory-descriptor semantics. It cannot demonstrate skill quality lift, so it is classified `smoke` / `ceiling`; no three-attempt calibration is warranted.

## Matched results

| Arm | Reward | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 76,183 | $0.099214 | 1m 37s |
| Original skill (`476bfc8`) | 1.0000 | 116,097 | $0.203105 | 2m 01s |
| Current skill (`d247a09`) | 1.0000 | 114,773 | $0.197094 | 2m 03s |

Current-skill changes:

- Versus no skill: 50.7% more tokens, 98.7% higher cost, and 26.8% longer runtime at unchanged quality.
- Versus the original skill: 1.1% fewer tokens, 3.0% lower cost, and 1.7% longer runtime at unchanged quality.

These are directional efficiency results from one attempt. They provide no reason to add task-specific descriptor instructions to the skill.

## Classification and next gate

Retain the task as deterministic correctness smoke coverage. Use `onednn-framework-blocked-layout` and the live `onednn-benchdnn-no-ref-memory` incident for skill-quality or efficiency evidence. Do not spend more attempts on this task unless the prompt, skill, or model changes materially.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `d247a090bc392cc2ce6fbb600ddbca707e7e5805`.
- Comparison prefix: `onednn-matmul-calibration-20260814`.
- Raw comparison: `harbor-jobs/onednn-matmul-calibration-20260814-comparison.md`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onednn-matmul-calibration-20260814-noskill)
- [Original skill](http://127.0.0.1:8080/jobs/onednn-matmul-calibration-20260814-previous)
- [Current skill](http://127.0.0.1:8080/jobs/onednn-matmul-calibration-20260814-candidate)
