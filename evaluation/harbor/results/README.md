# Retained Harbor evidence

This directory is the reviewable index for evaluator decisions. Raw `harbor-jobs/` directories remain ignored because they may contain trajectories, machine provenance, or access-controlled details. A retained summary records the evaluator revision, task scope, agent and model, runner, outcome, and raw-record authority.

## Active evidence authority

| Evidence | Evaluator revision | Task scope | Agent / model | Runner | Outcome and raw authority |
| --- | --- | --- | --- | --- | --- |
| [oneCCL zero-count topology source fixture](2026-08-27-oneccl-zero-count-fixture.md) | pending commit | `oneccl-zero-count-topo-alltoallv` | Oracle / no model | GLOW, WSL and Windows Docker Desktop | Harbor 0.20.0: 1/1 reward 1.0, zero errors; baseline calibration reward 0. Local result SHA-256 `B3224A63FAEC5BC0EC1A9F5C4059FCB9113577111561128EA7F079AABB019B96`. This is source-fixture evidence, not an Aurora hardware reproduction. |
| [GLOW container-trust repair](2026-08-26-glow-container-trust.md) | worktree equivalent to `993e3c0`, merged as `8318627` | Standard 35-task oracle smoke | Oracle / no model | GLOW, Windows Docker Desktop | 35/35 reward 1.0, zero errors. Local retained job `harbor-jobs/uxl-oracle-smoke-ca-fixed`; result SHA-256 `69857C6F06BB27E3AA2793985D480EFA3BB6565572B8347F63D37089A1412377`. |
| [SYCL/oneDNN runtime activation](2026-08-25-sycl-onednn-runtime-activation.md) | `60c8293` | `sycl-onednn-threading-runtime-composition` | Oracle / no model | GitHub-hosted Ubuntu | 1/1 reward 1.0, zero errors. Public [workflow run 33020529229](https://github.com/uxlfoundation/skills/actions/runs/33020529229) and its retained artifact are authoritative. |
| Windows/WSL GPU qualification | `884bc80bff12c4a61adb5c7e2127338a55e6e1fc` | `sycl-device-discovery-windows-wsl` | Oracle / no model | `private-wsl-GLOW` | 1/1 reward 1.0. Access-controlled workflow run `32846295857`; local retained job `harbor-jobs/uxl-windows-wsl-intel-gpu-oracle`; result SHA-256 `3D41E1B1D1CCD60C965DBD72909887AF490F957B94833F5D987635FAD224B94E`. |
| Release-candidate hosted smoke | `9cc58718fe4145e75aabb22b0edaf48e94eb4851` | Standard 35-task oracle smoke | Oracle / no model | GitHub-hosted Ubuntu | 35/35 reward 1.0. Public [workflow run 32882435717](https://github.com/uxlfoundation/skills/actions/runs/32882435717) is the baseline authority. |

The dated Markdown files below this index retain design, sourcing, calibration, activation, invalid-run, and go/no-go decisions. They are historical review records, not all current release authorities.

## Retention policy

Retain raw jobs when they are promotion evidence, paid/model-bearing comparisons, difficult hardware reproductions, or the current release oracle. Before removing a superseded raw job:

1. confirm a tracked summary or durable CI artifact exists;
2. record revision, task, agent/model, runner, result, and excluded infrastructure failures;
3. retain a SHA-256 for any local raw result that remains authoritative; and
4. quarantine the directory before permanent deletion when practical.

Routine retries, failed provisioning attempts, focused spot checks superseded by a full clean run, and duplicate local copies of durable CI artifacts are disposable. Never publish raw trajectories or provenance from private machines to the public dashboard without review.
