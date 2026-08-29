# UXL skills program status — 2026-08-26

## Outcome

The repository-resident work in the resumed plan is complete and reviewable. The UXL Skills Evaluator now reports 40 of 51 tasks implemented, the first agent-framework reference workload is reproducible, a real SYCL/oneDNN maintainer incident is executable, and the expensive task has a GitHub-hosted health workflow.

## Delivered

- Release baseline and ranked evaluation backlog.
- Current release/ownership source checks for oneTBB, oneDNN, and oneDAL, plus review packets for all eight skills.
- Maintainer review packets for the three strongest promotion candidates.
- Deterministic short-turn, tool-fan-out, and retrieval-heavy agentic workloads.
- LangGraph framework adapter with correctness, cancellation, exception, identity, and stage-timing checks.
- oneDAL nearest-neighbor prototype retained as a measured no-go on the tiny fixture; no performance benefit is claimed.
- `sycl-onednn-threading-runtime-composition`, sourced from oneDNN issue 2959 and verified against pinned oneDNN 3.6.1 and oneAPI 2026.1.0 inputs.
- Weekly, manually dispatchable, pull-request-aware GitHub-hosted oracle workflow for the new toolchain task.
- Dashboard data and rendered-page contracts updated to 40 implemented and 11 planned tasks.

## Verification

- Catalog, eval, Harbor-suite, capability-matrix, answer-checker, wrapper, and skill validation pass.
- 69 Python tests pass; two platform-dependent tests skip as designed.
- Dashboard lint, static export, and three rendered-page tests pass.
- 122 external links plus all local links pass with the CI-matching Python 3.12 runtime.
- Direct incident proof: mixed runtime failed 12/12; coherent OpenMP passed 20/20.
- Harbor task proof: one trial, zero exceptions, reward 1.0.
- GLOW local release proof after the container trust repair: 35 trials, zero errors, reward 1.0 on every standard smoke task.

The GLOW container trust repair imports only the approved Windows HTTPS-inspection root's public certificate into affected Linux image builds. TLS verification remains enabled; no `trusted-host` or verification bypass is used.

## Remaining external gates

- Assign people and dates, send the prepared review packets, and record maintainer decisions.
- Run matched no-skill, previous-skill, and candidate-skill model trials for promotion candidates.
- Add real oneCCL incident coverage.
- Qualify additional vendor/device and distributed lanes before making cross-platform support or performance claims.
- Revisit the oneDAL agentic pilot only with a larger quality-scored corpus and conversion-inclusive measurements.

These are governance, model-access, incident-sourcing, or hardware gates. They are intentionally visible as unfinished and are not substituted with synthetic evidence.
