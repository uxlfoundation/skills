# Hosted-toolchain tier audit: 2026-08-14

## Outcome

All evaluator tasks intended for the lightweight default hosted/free-runner suite are now implemented. Two remaining planned tasks can use generic hosted CPU hardware but require a substantial SYCL compiler/runtime/backend stack: `onemath-dispatch-overhead-benchmark` and `sycl-compile-time-backend-link`. They are now classified `hosted-toolchain`, distinct from both the lightweight default suite and target-hardware tasks.

This is an operational distinction, not evidence that the skills or failures are hardware-specific. The task guidance remains hardware-agnostic; the extra requirement is only the environment needed to compile and execute authentic SYCL/oneMath paths.

## Evidence

The [oneMath project requirements](https://github.com/uxlfoundation/oneMath#support-and-requirements) specify a SYCL compiler for host API use and linkage to the oneMath runtime or backend wrappers. The [DPC++ build guide](https://uxlfoundation.github.io/oneMath/building_the_project_with_dpcpp.html) also requires Intel or Open DPC++ plus backend dependencies; its generic BLAS path is experimental and may download additional header-only libraries.

The current evaluator host has no `icpx`, `icx`, `dpcpp`, or Clang SYCL compiler and no reusable SYCL/oneMath execution image. Pulling a large unpinned toolkit image into the lightweight suite would increase disk, setup time, and CI variance without improving target-hardware evidence.

## Portfolio tiers

| Tier | Implemented | Planned | Meaning |
| --- | ---: | ---: | --- |
| Lightweight hosted/container | 35 | 0 | Runs with the current default free-runner dependencies. |
| Hosted toolchain | 0 | 2 | Generic CPU hardware; opt-in pinned SYCL compiler/runtime/backend image. |
| Target hardware/distributed | 1 manual probe | 11 | Requires a device, target CPU/GPU, or distributed topology for a valid claim. |

The portfolio remains 36 of 49 tasks implemented. The 13 planned tasks now have explicit infrastructure ownership: two toolchain-tier tasks and eleven target-hardware tasks.

## Next gate

Select and pin one supported SYCL toolchain image, record its compressed and expanded size plus cold-start time, and implement `sycl-compile-time-backend-link` first. Reuse that environment for oneMath only if it can also provide an authentic CPU backend without an unbounded dependency build. Keep both jobs opt-in or scheduled until their setup cost is acceptable.
