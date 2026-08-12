# oneDNN benchdnn no-reference-memory incident: 2026-08-12

This milestone promotes oneDNN issue [#5732](https://github.com/uxlfoundation/oneDNN/issues/5732), fixed by [PR #5735](https://github.com/uxlfoundation/oneDNN/pull/5735), into live hosted-CPU coverage. The task reproduces a fused-convolution `benchdnn` crash in run and simulation modes, requires a source repair, and verifies the original descriptor plus a hidden alternate shape.

## Reproduction and portability

The upstream PR head is pinned at `371711c6d09742d9a5a536c1ae54156ff33018bc`; its pre-fix parent is `edc887bb71e405404dff49f8e29de7721f1e1720`. The exact maintainer descriptor crashed before the fix and passed after the accepted two-line guard prevented reference-memory work in modes that disable reference memories.

The public report used an AArch64 Neoverse V1 system. Native reproduction on an x86-64 Intel CPU proved the defect was not architecture-specific. A second audit set `ONEDNN_MAX_CPU_ISA=AVX2`: the untouched task still failed and the repair still passed using AVX2 implementations. The task image now fixes that AVX2 ceiling so its verifier does not depend on AVX-512 or a particular implementation name.

| Check | Result |
| --- | ---: |
| Public descriptor, untouched `R` and `S` | Both segfault |
| Hidden alternate shape, untouched `R` and `S` | Both segfault |
| AVX2 accepted repair | All four executions pass |
| Direct baseline reward | 0 |
| Direct oracle reward | 1 |
| Final Harbor oracle | Reward 1; 1 trial; 0 exceptions |
| Hardware | Generic hosted x86-64 CPU with AVX2 ceiling |

## Evaluator design

The environment builds the exact pre-fix oneDNN revision and upstream `benchdnn` harness in the image layer. Trials therefore perform only an incremental rebuild of the modified source. The verifier permits changes only to `tests/benchdnn/conv/conv_dw_fusion.cpp`, runs the public and hidden descriptors in both affected modes, and checks successful harness summaries and performance-report output without requiring a hardware-specific implementation string or timing threshold.

This is correctness-oriented triage of a benchmark harness, not a performance qualification. The measured times are deliberately not compared or reported as speedups.

The oneDNN skill now directs agents to preserve the descriptor and mode, classify create/fill/reorder/execute/compare/report phases, capture verbose implementation evidence, and respect the no-reference-memory contract before interpreting benchmark output.

## Portfolio impact and next step

The portfolio remains 49 planned tasks and now has 24 implemented. oneDNN has two implemented tasks, including its first task that is live, runs reproduce/investigate/repair/verify, and comes from a maintainer incident. Across the portfolio, four tasks now meet that complete real-world triage standard.

The task remains `uncalibrated`. Its next gate is a matched no-skill, previous-skill, and candidate-skill calibration. Because the upstream fix is small, it may become a ceiling task; calibration must measure verified success and token cost before treating it as evidence of skill value.

## Provenance

- Source issue: oneDNN #5732.
- Accepted repair: oneDNN PR #5735.
- Pre-fix revision: `edc887bb71e405404dff49f8e29de7721f1e1720`.
- Fixed revision: `371711c6d09742d9a5a536c1ae54156ff33018bc`.
- Harbor: 0.20.0.
- Final job: `harbor-jobs/onednn-benchdnn-oracle-avx2-20260812`.
