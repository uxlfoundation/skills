# Coverage wave 3: 2026-08-08

This wave adds three executable tasks for the largest remaining discriminating gaps in oneCCL, SYCL build/debug, and performance validation. The portfolio now implements 17 of 49 planned tasks across all eight skills.

## Added tasks

| Skill | Task | What success demonstrates |
| --- | --- | --- |
| `uxl-oneccl` | `oneccl-async-allreduce-wait` | Preserves asynchronous collective buffer lifetime, waits every event before consumption, bounds in-flight work, and returns deterministic ordered results. |
| `uxl-sycl-build-debug` | `sycl-selector-silent-cpu-fallback` | Fails closed unless selector, device identity, backend, completion, asynchronous-error, workload, and deterministic-result evidence prove the intended runtime path. |
| `uxl-performance-validation` | `performance-floating-reduction-tolerance` | Applies combined absolute/relative tolerance without truncating inputs or discarding invalid numerical evidence. |

All three tasks use hidden behavioral datasets. Their misleading starters are deliberately plausible but unsafe: one reuses live collective buffers without waiting, one accepts incomplete SYCL device evidence, and one ignores relative tolerance while silently truncating or filtering inputs.

## Development probes

One matched no-skill/skill attempt was run for each task. The SYCL verifier initially required one exact nested output shape even though the instruction allowed the selector to appear as normalized device evidence. Both SYCL artifacts were substantively correct and failed only because they included that extra selector field. The audited verifier now accepts the optional normalized selector while retaining every device, completion, error, workload, result, and malformed-input check; both original artifacts then pass, while the misleading starter remains rejected.

| Skill | Task | Audited baseline | Audited skill | Difference | Classification |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-oneccl` | `oneccl-async-allreduce-wait` | 1.0000 | 1.0000 | 0.0000 | Smoke/ceiling |
| `uxl-sycl-build-debug` | `sycl-selector-silent-cpu-fallback` | 1.0000 | 1.0000 | 0.0000 | Smoke/ceiling |
| `uxl-performance-validation` | `performance-floating-reduction-tolerance` | 1.0000 | 1.0000 | 0.0000 | Smoke/ceiling |

All six agent trials completed without exceptions. None advances to three-attempt calibration because no task showed directional headroom.

| Task | Arm | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: |
| oneCCL async wait | No skill | 70,550 | 63,232 | 2,158 | $0.132946 |
| oneCCL async wait | `uxl-oneccl` | 106,527 | 86,272 | 2,975 | $0.233661 |
| SYCL device proof | No skill | 153,342 | 130,816 | 5,775 | $0.351288 |
| SYCL device proof | `uxl-sycl-build-debug` | 139,342 | 115,712 | 5,951 | $0.354536 |
| Performance tolerance | No skill | 127,027 | 109,568 | 4,126 | $0.265859 |
| Performance tolerance | `uxl-performance-validation` | 218,853 | 184,576 | 9,614 | $0.552093 |

## Validation

- Capability manifest: 8 skills, 49 planned tasks, 17 implemented.
- Unit tests: 24 passed, including oracle-pass and starter-rejection coverage for every new verifier.
- Eval validation: 26 cases passed.
- New-task Harbor oracle: 3/3 trials, zero exceptions, reward 1.0.
- Structured-answer checkers: 8 task-local copies synchronized with the shared engine.
- External and local link checks passed.

Harbor oracle jobs:

- `uxl-oracle-coverage-wave3`
- `uxl-oracle-coverage-wave3-audited`

Raw jobs remain in the ignored local `harbor-jobs` directory. Inspect results with `harbor view harbor-jobs` and inspect task prompts and verifier files with `harbor view evaluation/harbor/tasks --tasks --port 8081`.

## Reproduction and provenance

- Harbor: `0.20.0`
- Agent: `codex`
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Codex CLI in trial images: `0.144.4`
- Attempts per arm: `1`
- Concurrency: `1`
- Task and skill starting revision: `e281eea`
- Audited verifier revision: this report's repository revision

Jobs used for the probes:

- Shared no-skill job: `coverage-wave3-baseline-gpt56-probe`
- oneCCL skill: `coverage-wave3-oneccl-skill-gpt56-probe`
- SYCL skill: `coverage-wave3-sycl-skill-gpt56-probe`
- Performance skill: `coverage-wave3-performance-skill-gpt56-probe`

The two SYCL job result files retain the initial raw reward of 0.0 for historical integrity. Their artifacts produce reward 1.0 under the audited verifier described above.

## Calibration state and next gate

The three tasks are retained as executable smoke coverage with calibration state `ceiling`. The portfolio still reserves at least two planned discriminating tasks per skill; `performance-profile-after-regression` is promoted in the plan to replace the performance task that reached ceiling.

The next coverage wave should favor less-prescriptive, multi-artifact tasks that require domain-specific diagnosis and repair rather than restating the full algorithm in the prompt: an actual distributed or trace-driven oneCCL failure, a CMake/link/runtime SYCL fixture, and a transfer-scope or profiling investigation. Those tasks still need deterministic success criteria, but the agent should have to derive the repair from evidence.

The async-completion contract follows oneCCL's documented benchmark behavior: distinct buffers may be in flight and explicit waits complete each collective. The device-proof contract follows the current SYCL selector and device-query model and uses the current `ONEAPI_DEVICE_SELECTOR` syntax. See the [oneCCL benchmark guide](https://uxlfoundation.github.io/oneCCL/benchmark-guide/benchmark.html), [SYCL device-selector reference](https://github.khronos.org/SYCL_Reference/iface/device-selector.html), [SYCL device reference](https://github.khronos.org/SYCL_Reference/iface/device.html), and [DPC++ environment-variable documentation](https://intel.github.io/llvm/EnvironmentVariables.html).
