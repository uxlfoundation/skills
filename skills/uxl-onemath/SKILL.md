---
name: uxl-onemath
description: "Use for oneAPI Math Library (oneMath) work: BLAS, LAPACK, RNG, DFT, and sparse BLAS domain selection; SYCL queues; runtime dispatch; compile-time backend selectors; device API guidance; backend setup for Intel, NVIDIA, AMD, Arm, Netlib, generic SYCL, and portFFT; CMake/linking and portability troubleshooting."
---

# UXL oneMath

## Purpose

Help an agent build portable oneMath code that targets the right domain, usage model, compiler, and backend without confusing oneMath with Intel oneMKL.

## First Pass

1. Identify the domain: BLAS, LAPACK, RNG, DFT, or sparse BLAS.
2. Identify the hardware target and compiler: Intel CPU/GPU, NVIDIA GPU, AMD GPU, Arm CPU, or generic SYCL device.
3. Choose host API runtime dispatch, host API compile-time dispatch, or the RNG device API.
4. Check the current support matrix before giving exact backend or OS claims.
5. Read local CMake and existing examples before editing build files.
6. For build, link, or backend-extension tasks, load the relevant reference below before acting.

## Usage Model Decision

- Use runtime dispatch when the application should link oneMath once and load the needed backend dynamically based on device vendor.
- Use compile-time dispatch when the application knows the backend at build time, needs static linking, or wants explicit `backend_selector` control.
- Use RNG device API when random generation is called inside a SYCL kernel and the API supports that path.
- Use the cross-cutting `uxl-sycl-build-debug` skill for compiler, target, device discovery, or runtime loader failures.

## Implementation Workflow

1. Write the math contract first: operation, layout convention, precision, dimensions, leading dimensions, batch shape, RNG engine/distribution, or transform placement.
2. Select a backend supported for the requested domain and hardware.
3. Keep SYCL queue ownership explicit. Do not silently create queues if the surrounding code already owns execution and dependencies.
4. Preserve event dependencies for asynchronous calls.
5. Update build logic with the exact libraries required by the selected dispatch mode.
6. Validate with small known-answer inputs, then representative problem sizes.

## Gotchas

- oneMath is an open source implementation and interface layer; Intel oneMKL is one possible backend/product. Name them precisely.
- Backend support differs by domain, compiler, OS, and hardware. Check current docs before making compatibility claims.
- Runtime dispatch assumes dynamic backend libraries are available at runtime.
- Compile-time dispatch requires linking the backend wrapper libraries explicitly.
- Leading dimensions, matrix layout, and batch strides are part of correctness, not tuning trivia.
- Small examples validate correctness; they rarely prove acceleration.

## Output Contract

When delivering oneMath work, include:

- Domain and routine family.
- Chosen usage model and backend.
- Compiler, link, and runtime assumptions.
- Correctness test and performance validation plan.
- Any unsupported or unverified backend combinations.

## References

Read [official sources](references/official-sources.md) for support matrices, build flows, compiler selection, and backend-specific limitations.

Load only the reference needed for the task:

- [Usage models](references/usage-models.md): runtime dispatch, compile-time dispatch, host API, and RNG device API choices.
- [Build and linking](references/build-and-linking.md): compiler choice, CMake targets, backend flags, and runtime loader checks.
- [Backend integration](references/backend-integration.md): adding a third-party backend to oneMath.
- [Common failures](references/common-failures.md): concise triage for common oneMath agent mistakes.
