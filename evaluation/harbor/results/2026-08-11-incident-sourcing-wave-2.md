# Maintainer incident sourcing: wave 2

This wave applied the reproducibility gate to the next two public candidates from wave 1. oneMath #623 was promoted into durable hosted-CPU smoke coverage after its pinned pre-fix source failed reliably and the accepted repair passed. oneDPL #2296 was not promoted: the failure is real, but the affected code path depends on an Intel compiler configuration that is not present in the lightweight free-runner environment.

## Decision ledger

| Skill | Incident | Evidence | Decision |
| --- | --- | --- | --- |
| `uxl-onemath` | [oneMath #623](https://github.com/uxlfoundation/oneMath/issues/623), fixed by [PR #625](https://github.com/uxlfoundation/oneMath/pull/625) | The pinned pre-fix public header failed in 3 of 3 runs with the reported missing `namespace_alias.hpp`; the upstream-equivalent repair and Harbor oracle passed. | **Verified and implemented** as `onemath-deprecated-header-include`, role `smoke`. |
| `uxl-onedpl` | [oneDPL #2296](https://github.com/uxlfoundation/oneDPL/issues/2296), fixed by [PR #2371](https://github.com/uxlfoundation/oneDPL/pull/2371) | GCC with the normal oneTBB and OpenMP host paths passed before the fix. Simulating the Intel compiler feature branch reproduced the reverse-iterator compile error before the fix and passed after it, but that is not an authentic compiler reproduction. | **Deferred to a toolchain tier**; retain `origin: unassigned` and do not claim live maintainer-incident coverage. |

## Implemented oneMath task

`onemath-deprecated-header-include` pins oneMath immediately before the accepted fix and preprocesses the deprecated public compatibility header against the installed include tree. The agent must preserve the compatibility entry point, its domain includes, and the deprecated namespace alias while repairing the incorrect relative include path. Read-only verifier inputs prevent solving the task by changing the consumer.

The task vendors the two exact affected upstream headers and stubs unrelated domain headers. Its build therefore preserves the reported preprocessing failure without downloading GitHub source during evaluation.

| Check | Result |
| --- | ---: |
| Pinned pre-fix baseline | Reward 0 in 3 of 3 runs |
| Baseline diagnostic | `fatal error: namespace_alias.hpp: No such file or directory` |
| Direct oracle repair | Reward 1 |
| Harbor oracle | Reward 1; 1 trial, 0 exceptions |
| Required hardware | Generic hosted CPU |
| Evaluation role | Smoke; expected low model-separation headroom |

The oneMath skill now tells agents to prefer `oneapi/math.hpp` for new work while preserving supported compatibility includes and diagnosing installed-tree or packaging failures before changing downstream consumer code.

## oneDPL deferral

The affected oneDPL source and accepted fix were confirmed, but an evaluator task should reproduce the failure with the real triggering compiler rather than manufacture that environment with feature macros. Adding the Intel compiler and its runtime to every default smoke run would materially increase setup and download cost. A scheduled toolchain tier can carry that dependency without burdening the lightweight default suite.

## Portfolio effect and next gate

The portfolio remains 49 planned tasks and now has 22 implemented tasks. Two implemented tasks meet the full standard of a live reproduce/investigate/repair/verify workflow sourced from a verified maintainer incident: `onetbb-join-node-ordering` and `onemath-deprecated-header-include`.

During full-suite validation, the floating `python:3.12-slim` base advanced to an image that produced `exec format error` on this Docker host. The 15 affected task environments now use a digest-pinned Bookworm variant, preventing an unrelated upstream base-image change from silently breaking evaluator reproducibility.

The next candidate is the cgroup-aware oneTBB concurrency incident tracked as `uxl-performance-validation` coverage. Before implementation, it must prove that the runner exposes a meaningful host-count versus container-quota mismatch and that a correctness-oriented verifier can avoid timing noise. The new oneMath smoke task should also receive a matched no-skill/previous-skill/candidate calibration; a ceiling result is acceptable because the task exists primarily as regression and workflow coverage.
