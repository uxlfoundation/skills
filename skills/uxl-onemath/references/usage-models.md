# oneMath Usage Models

Use this reference when deciding how an application should call oneMath.

Source anchors:

- oneMath README usage models: https://github.com/uxlfoundation/oneMath
- oneMath CMake consumption docs: https://uxlfoundation.github.io/oneMath/using_onemath_with_cmake.html
- oneMath RNG device routines: https://uxlfoundation.github.io/oneMath/spec/domains/rng/device_api/device-routines.html

## Runtime Dispatch

Use runtime dispatch when the application should link against the oneMath selector layer and load the required backend dynamically based on device vendor.

Agent checklist:

- Link the broad oneMath library target or library, not a single backend wrapper.
- Confirm backend dynamic libraries are findable at runtime.
- Confirm device selection is explicit enough that the intended backend is selected.
- Report that runtime dispatch trades explicit build-time backend selection for deployment flexibility.

## Compile-Time Dispatch

Use compile-time dispatch when the application knows the backend at build time or needs explicit `backend_selector` control.

Agent checklist:

- Use a backend selector such as `oneapi::math::backend_selector<oneapi::math::backend::<backend>>`.
- Link the domain/backend-specific target or wrapper library.
- Confirm the compiler and backend library combination is supported.
- Keep queue ownership explicit.

## RNG Device API

Use RNG device API only for RNG work intended to run inside SYCL kernels and currently supported by the oneMath RNG device API.

Agent checklist:

- Include the RNG device API header, not just the host API.
- Ask for generator, distribution, seed/reproducibility requirements, and target backend.
- Validate with deterministic seeds where possible.

## Response Pattern

When asked which model to use, answer with:

1. Recommended model.
2. Why the other model is less suitable.
3. Required compiler, CMake target, and runtime-library assumptions.
4. Correctness and benchmark validation plan.
