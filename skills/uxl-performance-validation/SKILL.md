---
name: uxl-performance-validation
description: "Use for cross-UXL correctness and performance evidence: creating benchmark plans, comparing CPU/GPU or old/new code paths, selecting representative problem sizes, accounting for transfer/setup costs, measuring asynchronous work correctly, setting numerical tolerances, reporting speedups, profiling bottlenecks, and preventing unsupported performance claims."
---

# UXL Performance Validation

## Purpose

Help an agent turn "this should be faster" into repeatable evidence: correctness first, then fair measurement, then a bounded claim.

## Validation Workflow

1. Define the user-visible contract: outputs, ordering, tolerances, resource limits, and failure behavior.
2. Establish a baseline before changing code.
3. Choose representative problem sizes and at least one small deterministic correctness case.
4. Separate setup, data transfer, allocation, warmup, steady-state compute, synchronization, and teardown when possible.
5. Measure asynchronous work with explicit synchronization or events.
6. Run multiple iterations and report variance or confidence.
7. Profile only after a repeatable regression or speedup is visible.

## Library-Specific Hooks

- oneDNN: prefer `benchdnn` or existing primitive benchmarks when available.
- oneMath: state whether timing includes queue creation, backend dispatch, transfers, and events.
- oneDAL: include data conversion and metric parity, especially for scikit-learn acceleration.
- oneTBB: state thread limits, input size, grainsize, affinity, and serial baseline.
- oneDPL: state host/device policy, data location, transfers, and synchronization.
- oneCCL: state rank count, topology, tensor size, collective sequence, and worker/plugin settings.

## Gotchas

- Small problem sizes often validate correctness but do not show acceleration.
- Floating point reductions can differ because of non-associativity. Use tolerances and explain them.
- GPU timing without synchronization measures launch overhead, not completion.
- Debug builds, thermal throttling, affinity, and background load can swamp real effects.
- Do not compare an optimized library path to an intentionally naive baseline unless the claim says so.

## Report Template

```markdown
## Correctness
- Reference:
- Inputs:
- Tolerance:
- Result:

## Performance
- Baseline:
- Candidate:
- Hardware/software:
- Problem sizes:
- Timing method:
- Iterations:
- Result:

## Claim
- Supported claim:
- Limitations:
- Next validation:
```

## Output Contract

When delivering validation work, include:

- Baseline and candidate commands.
- Correctness comparison method.
- Timing method and synchronization.
- Result table.
- A conservative claim and limitations.

## References

Read [benchmark contract](references/benchmark-contract.md) when designing a new benchmark or reviewing a performance claim.
