# Evaluation priorities — 2026-08-25

Update on 2026-08-29: priorities 3 and 4 are implemented. The LangGraph reference workload and oneDAL adapter retain a correctness-passing no-go result for the tiny corpus, while `sycl-onednn-threading-runtime-composition` reproduces a pinned maintainer incident and passes its Harbor oracle. Review packets now exist for all eight skills; priorities 1 and 2 still require human owners and maintainer decisions.

This backlog ranks work by promotion value and evidence quality. It distinguishes work we can execute on GitHub-hosted infrastructure from work that first needs a maintainer incident, a target machine, or a human review.

## Priority order

| Priority | Work | Why now | Can execute now? | Completion evidence |
| --- | --- | --- | --- | --- |
| 1 | oneTBB maintainer review and promotion calibration | All 7 declared tasks are implemented and two retain headroom. Governance, not task count, is the largest gap. | Packet and local checks: yes. Review and promotion trials: human/model access required. | Maintainer approval plus five matched attempts per arm and no policy regression. |
| 2 | oneDNN and oneDAL maintainer reviews | Both implement 5 of 6 tasks and have incident-sourced executable evidence. Early review can correct scope before more hardware work. | Packet and local checks: yes. Review: human gate. | Recorded project decisions and synchronized follow-up changes. |
| 3 | Agentic reference workload and framework adapter | This is the program's missing cross-project proof point and creates a concrete performance-validation target. | Yes, on hosted CPU with deterministic fixtures. | Reproducible correctness, failure-path, stage timing, and baseline results. |
| 4 | `sycl-onednn-threading-runtime-composition` | It is the only planned target that can run on a hosted toolchain without vendor hardware. | Design/build: yes. Full toolchain run: GitHub-hosted workflow. | Live reproduce/repair/verify task with retained toolchain provenance. |
| 5 | oneCCL and SYCL incident sourcing | Both suites need authentic end-to-end maintainer failures for promotion-quality evidence. | Candidate research: yes. Acceptance and details: maintainer gate. | Accepted incident or upstream regression mapped to a reproducible task. |
| 6 | Performance-validation device tasks | The suite has no discriminating headroom today; transfer scope is broadly useful across vendors. | Fixture/contract: yes. Credible result: target-device lane required. | Correctness-gated task on at least two declared platform lanes. |
| 7 | oneMath and oneDPL target-device tasks | These close large project-specific gaps but should follow the shared device-methodology contract. | Fixture/contract: yes. Credible result: target device required. | Live tasks with device/backend provenance and matched calibration. |
| 8 | oneCCL distributed performance task | Highest infrastructure cost and depends on a stable multi-rank lane. | No. | Reproducible multi-rank environment, topology provenance, and retained results. |

## Execution rule

Do not substitute a synthetic fixture for a required maintainer incident or claim a hardware result from a hosted answer-quality task. While external gates are pending, continue with deterministic hosted work, review preparation, and target-lane contracts. Keep all blocked tasks visible as `planned` in `evaluation/harbor/suites.json`.
