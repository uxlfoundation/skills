# Calibration-state audit: 2026-08-13

## Outcome

The portfolio previously used `uncalibrated` for both tasks that had never run and tasks that had valid matched evidence but did not demonstrate skill value. This made evaluator health look worse and obscured useful negative controls. The manifest now includes `no-lift` for evaluated tasks with residual quality headroom but no durable skill advantage.

Four implemented task states are corrected from the evidence already recorded in coverage waves 1 and 2:

| Task | Evidence | Corrected state |
| --- | --- | --- |
| `oneccl-datatype-count-mismatch` | Three attempts per arm; skill mean `0.7333` versus baseline `0.7611` | `no-lift` |
| `sycl-loader-plugin-mismatch` | Matched screen tied at `0.8333` | `no-lift` |
| `performance-tiny-async-gpu-claim` | Matched screen tied at `0.8889` | `no-lift` |
| `performance-benchmark-report-repair` | Both arms reached `1.0000` | `ceiling` |

This leaves only `onetbb-join-node-ordering` among implemented tasks without a calibration classification.

## Current oneCCL audit

A new three-arm, one-attempt screen used `codex`, `gpt-5.6-sol`, medium reasoning, and serial execution. The raw Harbor rewards were `0.6667` without a skill, `0.7667` with the previous skill, and `0.8500` with the current skill. Manual artifact review found that most of this apparent difference came from wording-sensitive checks rather than missing technical content.

The rubric now accepts equivalent descriptions of out-of-bounds datatype access, oneCCL build/runtime versions, deterministic two- or four-rank reproducers, and rank-wide exact output checks. It still rejects all three answers' substantive omission: none defines a complete bounded benchmark across representative message sizes and topology with warmup/repetition controls.

Offline rescoring gives every arm `0.9167`:

| Arm | Audited reward | Total tokens | Cost | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 0.9167 | 62,683 | $0.128907 | 2m 55s |
| Previous skill (`476bfc8`) | 0.9167 | 145,647 | $0.269171 | 3m 06s |
| Current skill (`0c84d79`) | 0.9167 | 128,105 | $0.240288 | 3m 48s |

The previous and current oneCCL skill directories have the same Git tree, so their one-attempt difference is sampling variance rather than a skill change. Neither skilled arm reached the verified-success floor, and the current arm used 104.4% more tokens than no skill. This screen therefore agrees with the earlier three-attempt `no-lift` classification and does not justify more model runs.

## Interpretation

`No-lift` is not a task failure. These tasks still test useful contracts and can catch regressions, but they cannot support a claim that the present skill improves agent outcomes. They become candidates for task hardening, skill revision, or retirement—not candidates for automatic repetition.

## Reproduction

- Historical evidence: [coverage wave 1](2026-08-08-coverage-wave-1.md) and [coverage wave 2](2026-08-08-coverage-wave-2.md).
- Current oneCCL job prefix: `oneccl-datatype-calibration-20260813`.
- Raw current comparison: `harbor-jobs/oneccl-datatype-calibration-20260813-comparison.md`.
- Raw jobs are immutable; audited offline scores are the classification check.
