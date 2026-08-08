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

## Rubric audit

The initial answer artifacts exposed wording-sensitive false negatives in all three structured-answer rubrics. The audited rubrics now accept equivalent evidence such as structured byte-field names and rank-local records, `job id`/`input order` and a `serial golden`, and equivalent loader tracing, deployment, selector, warm-up, and bounded-claim wording. The changes preserve the substantive requirements: omitted synchronization, lifetime, rank-contract, loader, device-proof, and benchmark controls still fail their criteria.

The directional results below re-score the original artifacts with the audited rubrics. They select calibration candidates but are not promotion evidence.

| Skill | Task | Baseline | Skill | Difference | Probe decision |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-onetbb` | `onetbb-bounded-image-flow-graph` | 0.6944 | 1.0000 | +0.3056 | Advanced to calibration |
| `uxl-oneccl` | `oneccl-datatype-count-mismatch` | 0.8333 | 0.9167 | +0.0834 | Advanced to calibration |
| `uxl-performance-validation` | `performance-benchmark-report-repair` | 1.0000 | 1.0000 | 0.0000 | Smoke/ceiling candidate |
| `uxl-sycl-build-debug` | `sycl-loader-plugin-mismatch` | 0.8333 | 0.8333 | 0.0000 | Smoke/no-lift candidate |

## Calibrated summary

| Skill | Task | Baseline mean | Skill mean | Difference | State |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-onetbb` | `onetbb-bounded-image-flow-graph` | 0.6666 | 0.8611 | +0.1945 | Headroom |
| `uxl-oneccl` | `oneccl-datatype-count-mismatch` | 0.7611 | 0.7333 | -0.0278 | Smoke/no demonstrated lift |

The oneTBB task remains discriminating and is marked `headroom`. The oneCCL task completed the same three-attempt calibration but did not preserve its small probe lift, so it is retained as smoke coverage rather than evidence of skill value. The one-attempt performance and SYCL pairs also become smoke coverage; neither showed a reason to spend more calibration attempts.

## oneTBB three-attempt calibration

The two additional attempts per arm used the unchanged task, skill, and audited rubric. The first attempt in each arm is the original probe re-scored with that rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.6944, 0.7222, 0.5833 | 0.6666 | 169,398 | 135,168 | 4,689 | $0.379404 |
| `uxl-onetbb` | 1.0000, 0.8056, 0.7778 | 0.8611 | 440,996 | 364,288 | 10,188 | $0.871324 |
| Difference |  | +0.1945 |  |  |  |  |

All six trials completed without errors. The skill arm retained a meaningful mean advantage across repeated samples, confirming that the task has measurable headroom.

## oneCCL three-attempt calibration

The two additional attempts per arm used the unchanged task, skill, and audited rubric. The first attempt in each arm is the original probe re-scored with that rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.8333, 0.8333, 0.6167 | 0.7611 | 168,364 | 142,336 | 4,890 | $0.348008 |
| `uxl-oneccl` | 0.9167, 0.6000, 0.6833 | 0.7333 | 490,308 | 386,816 | 9,029 | $0.981738 |
| Difference |  | -0.0278 |  |  |  |  |

All six trials completed without errors. The difference is small and reversed direction after repetition. This task is useful for regression coverage, but it cannot support a claim that the current skill improves performance on this prompt.

## Validation

- Capability manifest: 8 skills, 49 planned tasks, 14 implemented.
- Unit tests: 22 passed.
- Structured-answer checkers: 8 task-local copies synchronized with the shared engine.
- New-task Harbor oracle: 4/4 trials, zero exceptions, reward 1.0.
- Full hosted Harbor oracle: 13/13 trials, zero exceptions, reward 1.0.
- Audited-rubric Harbor oracle: 3/3 changed structured tasks, zero exceptions, reward 1.0.
- External and local link checks passed.

Harbor jobs:

- `uxl-oracle-coverage-wave2`
- `uxl-oracle-smoke-wave2`
- `uxl-oracle-wave2-calibration`

Raw jobs remain in the ignored local `harbor-jobs` directory. Inspect them with `harbor view harbor-jobs` and inspect task instructions and verifier files with `harbor view evaluation/harbor/tasks --tasks --port 8081`.

## Reproduction and provenance

- Harbor: `0.20.0`
- Agent: `codex`
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Codex CLI in trial images: `0.144.4`
- Calibration attempts per arm: `3`
- Concurrency: `1`
- Task, instruction, and skill starting revision: `1e1a00a`
- Rubric revision: this report's repository revision

Jobs used for the development probes:

- Shared no-skill job: `coverage-wave2-baseline-gpt56-probe`
- oneTBB skill: `coverage-wave2-onetbb-skill-gpt56-probe`
- oneCCL skill: `coverage-wave2-oneccl-skill-gpt56-probe`
- Performance skill: `coverage-wave2-performance-skill-gpt56-probe`
- SYCL skill: `coverage-wave2-sycl-skill-gpt56-probe`

Jobs used for the additional calibration attempts:

- oneTBB baseline: `coverage-wave2-onetbb-baseline-gpt56-calibration-r2`
- oneTBB skill: `coverage-wave2-onetbb-skill-gpt56-calibration-r2`
- oneCCL baseline: `coverage-wave2-oneccl-baseline-gpt56-calibration-r2`
- oneCCL skill: `coverage-wave2-oneccl-skill-gpt56-calibration-r2`

## Next gate

Wave 2 establishes one new discriminating task and three new smoke tasks. The next coverage wave should implement another discriminating task for oneCCL, SYCL build/debug, and performance validation, favoring executable or artifact-based verification where practical. Promotion comparisons remain five matched attempts per arm under the manifest policy.

API-specific task details were checked against the current [oneTBB limiter-node specification](https://uxlfoundation.github.io/oneTBB/main/specification/source/flow_graph/limiter_node_cls.html), [oneCCL allreduce contract](https://uxlfoundation.github.io/oneCCL/api/operations/collective-operations/allreduce.html), and [DPC++ runtime environment-variable documentation](https://intel.github.io/llvm/EnvironmentVariables.html).
