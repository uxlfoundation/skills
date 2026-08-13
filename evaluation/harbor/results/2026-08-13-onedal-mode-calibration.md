# oneDAL mode-selection calibration: 2026-08-13

## Outcome

The `onedal-batch-online-distributed-choice` task is a quality ceiling under the current model. After auditing equivalent technical wording, the no-skill, original-skill, and current-skill answers all satisfy the full rubric. The current `uxl-onedal` skill used **181,244 tokens per verified success**, 44.2% fewer than the original catalog skill but 4.6% more than no skill.

This one-attempt development screen does not show that the current skill improves quality or token efficiency over the model alone. It does show that the current concise skill removed most of the original skill's token penalty. Additional attempts are not justified on this task unless the prompt or rubric is made more discriminating.

## Audited matched results

| Arm | Audited reward | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 173,283 | $0.304715 | 3m 06s |
| Original skill (`476bfc8`) | 1.0000 | 324,647 | $0.512140 | 3m 33s |
| Current skill (`2f74b7a`) | 1.0000 | 181,244 | $0.327598 | 3m 38s |

Candidate changes:

- Versus no skill: 4.6% more tokens per verified success, 7.5% higher cost, and 17.2% longer runtime.
- Versus the original skill: 44.2% fewer tokens per verified success, 36.0% lower cost, and 2.3% longer runtime.

## Verifier audit

The immutable Harbor jobs reported rewards of `0.7917`, `0.6667`, and `0.7917` for the no-skill, original-skill, and current-skill arms. Manual review found false negatives caused by literal phrasing assumptions in two rubric criteria:

- reference parity rejected phrases such as `trusted double-precision reference` even when the answer also fixed preprocessing, feature order, data type, covariance definition, outputs, and tolerances;
- fair benchmarking rejected equivalent repetition, variance, tail, and finalization language.

The task-local rubric now accepts these equivalent formulations while retaining all required evidence groups. A regression test covers the broader phrasing. Offline rescoring of the saved answer artifacts gives all three arms reward `1.0`. Raw Harbor results remain unchanged; the audited scores are the classification evidence.

## Classification and next gate

Classify the task as `ceiling`. Retain it as hardware-agnostic review coverage for choosing batch, online, or distributed computation and demanding parity and end-to-end measurement evidence. Do not use it as evidence that the current skill is better than no skill.

The next useful oneDAL investment is a harder task with independently phrased evidence or a live workflow where the model has room to fail. A future promotion claim should combine quality and token efficiency across multiple tasks rather than extrapolate from this ceiling screen.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `2f74b7abacb9ff7efae5b87da531d9e7977f2f6f` plus the audited rubric correction recorded with this report.
- Job prefix: `onedal-mode-calibration-20260813`.
- Raw comparison: `harbor-jobs/onedal-mode-calibration-20260813-comparison.md`.
