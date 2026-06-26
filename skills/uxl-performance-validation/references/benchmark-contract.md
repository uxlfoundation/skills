# Benchmark Contract

Use this checklist before accepting or writing a UXL performance claim.

## Correctness First

- Define the reference implementation.
- Define deterministic inputs or a fixed seed.
- Define tolerance and comparison method.
- Include at least one small case that is easy to inspect.
- Include at least one representative production-shaped case.

## Measurement

- Record hardware, OS, compiler, backend, library commit/version, build type, and runtime settings.
- Separate one-time setup from steady-state measurement where possible.
- Synchronize asynchronous device or communication work before stopping the timer.
- Warm up before measuring.
- Run multiple iterations and report median or distribution, not a single best time.
- Include data movement, conversion, allocation, dispatch, or synchronization costs when they are part of the user-visible workflow.

## Reporting

Use this compact table:

| Case | Baseline | Candidate | Speedup | Correctness | Notes |
| --- | --- | --- | --- | --- | --- |
| name | command/time | command/time | ratio | pass/fail/tolerance | caveats |

State the supported claim narrowly. Example: "1.4x faster for fp32 GEMM shape MxNxK on A100 with data already resident on device" is useful. "oneMath is 1.4x faster" is not.
