# 2026-08-25 Release-candidate ledger

Baseline commit: `9cc58718fe4145e75aabb22b0edaf48e94eb4851`

Release type: incubating catalog release candidate

Public evaluator: https://uxlfoundation.github.io/skills/

## Recorded state

- Eight published skills: seven `incubating` and one `pilot`.
- 51 declared Harbor tasks: 39 implemented and 12 planned.
- 9 implemented tasks retain measured headroom, 25 are at ceiling, 3 show no lift, and 2 hardware tasks require manual calibration.
- All eight skills still require owning-project or cross-project maintainer review. No skill is represented as reviewed or project-owned.
- oneTBB implements all 7 declared tasks. oneDNN and oneDAL each implement 5 of 6.
- The live UXL Skills Evaluator presents portfolio health, evaluation coverage, platform lanes, and methodology without treating a single hardware vendor as the default.

## Reproducibility evidence

GitHub Actions run [32882435717](https://github.com/uxlfoundation/skills/actions/runs/32882435717) completed successfully against the baseline commit. The run includes:

- catalog, skill, Harbor-suite, rendered-suite, answer-checker, wrapper-drift, and link validation;
- 64 unit tests;
- the 35-task Harbor oracle smoke run and reward-floor check;
- the SYCL probe and performance-summary helper smoke tests; and
- generation checks for all published agent wrappers.

The same commit is the source for the deployed GitHub Pages evaluator.

## Promotion state

This is a reproducible baseline, not a promotion record. Promotion remains blocked on:

- owning-project maintainer review;
- matched no-skill, previous-skill, and candidate-skill evidence at the required attempt count;
- remaining target-device, target-distributed, and hosted-toolchain tasks where applicable;
- a real maintainer incident or upstream regression for oneCCL and the cross-project SYCL suite; and
- hardware provenance for every hardware-dependent support or performance claim.

## Deferred work

- 12 planned Harbor tasks remain explicitly visible in `evaluation/harbor/suites.json`.
- The agentic reference workload and first framework adapter are not part of this baseline commit.
- Maintainer review packets are prepared separately and do not imply that a review has been requested or accepted.

This ledger pins the known-good state before the agentic-workload and maintainer-review workstream changes begin.
