# Evaluator reproducibility audit: 2026-08-10

The Harbor portfolio was migrated to schema version 2.0 so that capability coverage no longer implies full triage coverage. Every task now declares whether it reproduces live, uses a supplied fixture, or performs a review; where the scenario came from; which triage stages it exercises; and what hardware it requires.

## Portfolio baseline

| Measure | Count |
| --- | ---: |
| Total planned portfolio | 49 |
| Implemented tasks | 20 |
| Implemented live tasks | 9 |
| Implemented fixture or review tasks | 11 |
| Planned live tasks | 26 |
| Planned review tasks | 3 |
| Tasks declaring target hardware | 12 |
| Implemented target-hardware tasks | 1 |
| Real end-to-end triage tasks | 0 |

A real end-to-end task must be implemented, reproduce live, exercise reproduce, investigate, repair, and verify, and come from a maintainer incident or upstream regression. Existing executable tasks are constructed cases, so they remain useful implementation and workflow coverage but do not yet receive that credit.

## Component audit

| Skill | Implemented | Live implemented | Fixture implemented | Planned live | Target-hardware tasks | Unassigned live origins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `uxl-onednn` | 1 | 0 | 1 | 4 | 1 | 4 |
| `uxl-onemath` | 1 | 0 | 1 | 5 | 2 | 5 |
| `uxl-onedal` | 1 | 0 | 1 | 4 | 1 | 4 |
| `uxl-onetbb` | 6 | 4 | 2 | 1 | 0 | 1 |
| `uxl-onedpl` | 1 | 0 | 1 | 5 | 2 | 5 |
| `uxl-oneccl` | 3 | 1 | 2 | 2 | 2 | 2 |
| `uxl-sycl-build-debug` | 4 | 2 | 2 | 2 | 2 | 1 |
| `uxl-performance-validation` | 3 | 2 | 1 | 3 | 2 | 3 |

The 25 `unassigned` origins are deliberate gaps. They prevent planned task names from being mistaken for evidence-backed incidents before an owning project supplies or confirms a real reproducer.

## Environment decisions

- Twenty-three tasks are designed for live execution on generic hosted CPUs.
- Fourteen fixture or review tasks remain on hosted containers and do not claim reproduction or verification.
- Twelve tasks require target hardware or a target-distributed environment; only the manually dispatched SYCL device probe is currently implemented.
- Target-hardware declarations identify intended coverage but do not claim that runner capacity has been secured.

## Recommended next wave

First source one maintainer incident or upstream regression for every skill. Prefer cases that can run on free hosted CPUs before adding hardware operations. Current candidate task slots are:

| Skill | Candidate slot | Intended environment |
| --- | --- | --- |
| `uxl-onednn` | `onednn-convolution-fusion-parity` | Hosted CPU |
| `uxl-onemath` | `onemath-blas-leading-dimension` | Hosted CPU |
| `uxl-onedal` | `onedal-table-orientation-regression` | Hosted CPU |
| `uxl-onetbb` | `onetbb-legacy-api-migration` | Hosted CPU |
| `uxl-onedpl` | `onedpl-iterator-category-failure` | Hosted CPU |
| `uxl-oneccl` | `oneccl-plugin-rank-visibility` | Target distributed |
| `uxl-sycl-build-debug` | `sycl-compile-time-backend-link` | Hosted CPU |
| `uxl-performance-validation` | `performance-variance-and-outliers` | Hosted CPU |

The task slot is not binding if maintainer feedback identifies a more representative failure. Use `MAINTAINER_FAILURE_INTAKE.md` to capture the reproducer and hardware contract before implementation.

After each task is implemented, run matched no-skill, previous-skill, and candidate-skill arms. Quality is the gate; the primary efficiency result is cost per verified success, supported by uncached input, cached input, output tokens, runtime, and raw Harbor artifacts.
