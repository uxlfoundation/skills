# Coverage wave 3: 2026-08-08

This wave adds three executable tasks for the largest remaining discriminating gaps in oneCCL, SYCL build/debug, and performance validation. The portfolio now implements 17 of 49 planned tasks across all eight skills.

## Added tasks

| Skill | Task | What success demonstrates |
| --- | --- | --- |
| `uxl-oneccl` | `oneccl-async-allreduce-wait` | Preserves asynchronous collective buffer lifetime, waits every event before consumption, bounds in-flight work, and returns deterministic ordered results. |
| `uxl-sycl-build-debug` | `sycl-selector-silent-cpu-fallback` | Fails closed unless selector, device identity, backend, completion, asynchronous-error, workload, and deterministic-result evidence prove the intended runtime path. |
| `uxl-performance-validation` | `performance-floating-reduction-tolerance` | Applies combined absolute/relative tolerance without truncating inputs or discarding invalid numerical evidence. |

All three tasks use hidden behavioral datasets. Their misleading starters are deliberately plausible but unsafe: one reuses live collective buffers without waiting, one accepts incomplete SYCL device evidence, and one ignores relative tolerance while silently truncating or filtering inputs.

## Validation

- Capability manifest: 8 skills, 49 planned tasks, 17 implemented.
- Unit tests: 24 passed, including oracle-pass and starter-rejection coverage for every new verifier.
- Eval validation: 26 cases passed.
- New-task Harbor oracle: 3/3 trials, zero exceptions, reward 1.0.
- Structured-answer checkers: 8 task-local copies synchronized with the shared engine.
- External and local link checks passed.

Harbor job: `uxl-oracle-coverage-wave3`.

Raw jobs remain in the ignored local `harbor-jobs` directory. Inspect results with `harbor view harbor-jobs` and inspect task prompts and verifier files with `harbor view evaluation/harbor/tasks --tasks --port 8081`.

## Calibration state and next gate

The three tasks begin as `uncalibrated` and intended to be discriminating. Run one matched no-skill/skill attempt per task as a development probe. Advance any task with observed headroom to the manifest's three-attempt calibration; reclassify ceiling or no-lift tasks as smoke rather than using them to claim skill value.

The async-completion contract follows oneCCL's documented benchmark behavior: distinct buffers may be in flight and explicit waits complete each collective. The device-proof contract follows the current SYCL selector and device-query model and uses the current `ONEAPI_DEVICE_SELECTOR` syntax. See the [oneCCL benchmark guide](https://uxlfoundation.github.io/oneCCL/benchmark-guide/benchmark.html), [SYCL device-selector reference](https://github.khronos.org/SYCL_Reference/iface/device-selector.html), [SYCL device reference](https://github.khronos.org/SYCL_Reference/iface/device.html), and [DPC++ environment-variable documentation](https://intel.github.io/llvm/EnvironmentVariables.html).
