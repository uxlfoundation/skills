# Coverage wave 2: 2026-08-08

This wave adds four tasks selected from the largest gaps exposed by wave 1: a non-ceiling performance task, a oneTBB integration task, a oneCCL validation companion, and a SYCL runtime-proof companion.

## Added tasks

| Skill | Task | Track | What success demonstrates |
| --- | --- | --- | --- |
| `uxl-performance-validation` | `performance-benchmark-report-repair` | Executable | Produces correctness-gated, scope-specific median comparisons; rejects invalid, non-finite, or under-sampled claims. |
| `uxl-onetbb` | `onetbb-bounded-image-flow-graph` | Answer quality | Designs bounded admission, reliable token return, stage limits, and scheduler-aware resource validation. |
| `uxl-oneccl` | `oneccl-datatype-count-mismatch` | Answer quality | Diagnoses element-count/datatype contract violations and defines rank-local, memory-safe validation. |
| `uxl-sycl-build-debug` | `sycl-loader-plugin-mismatch` | Answer quality | Separates runtime loader failure from build phases and proves a coherent service deployment on the intended device. |

The performance task uses hidden behavioral datasets rather than keyword scoring. Its misleading starter mixes timing scopes, includes warmups, ignores correctness, and averages skewed samples; the oracle satisfies the full contract while the starter is rejected.

The answer-quality tasks use the shared grouped-rubric engine. Their reference answers satisfy every criterion and their unsupported-claim gates reject the central unsafe shortcuts.

## Validation

- Capability manifest: 8 skills, 49 planned tasks, 14 implemented.
- Unit tests: 22 passed.
- Structured-answer checkers: 8 task-local copies synchronized with the shared engine.
- New-task Harbor oracle: 4/4 trials, zero exceptions, reward 1.0.
- Full hosted Harbor oracle: 13/13 trials, zero exceptions, reward 1.0.
- External and local link checks passed.

Harbor jobs:

- `uxl-oracle-coverage-wave2`
- `uxl-oracle-smoke-wave2`

Raw jobs remain in the ignored local `harbor-jobs` directory. Inspect them with `harbor view harbor-jobs` and inspect task instructions and verifier files with `harbor view evaluation/harbor/tasks --tasks --port 8081`.

## Calibration state and next gate

All four tasks remain `uncalibrated`. Run one matched no-skill/skill attempt for each task as a development probe. Advance tasks with observed headroom to three attempts per arm; reclassify any near-ceiling task as smoke rather than using it to claim skill value.

API-specific task details were checked against the current [oneTBB limiter-node specification](https://uxlfoundation.github.io/oneTBB/main/specification/source/flow_graph/limiter_node_cls.html), [oneCCL allreduce contract](https://uxlfoundation.github.io/oneCCL/api/operations/collective-operations/allreduce.html), and [DPC++ runtime environment-variable documentation](https://intel.github.io/llvm/EnvironmentVariables.html).
