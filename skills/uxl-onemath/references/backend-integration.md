# oneMath Backend Integration

Use this reference when adding a third-party backend to oneMath.

Source anchor:

- Integrating a third-party library: https://uxlfoundation.github.io/oneMath/create_new_backend.html

## Naming

Follow the documented naming shape:

- `onemath_<domain>_<third-party-library-short-name>`
- Add a target-specific suffix only when the same third-party library needs multiple wrappers.

Examples:

- `onemath_rng_curand`
- `onemath_blas_mklcpu`
- `onemath_blas_mklgpu`

## Required Work Areas

A new backend is not just a wrapper file. Plan changes across:

- Public or detail headers declaring new backend entry points.
- Compile-time dispatch interface headers for the new backend.
- Backend enum and backend map entries.
- Wrapper source files.
- Runtime-dispatch wrapper table when building dynamic dispatcher support.
- CMake option such as `ENABLE_<BACKEND>_BACKEND`.
- Backend subdirectory and `CMakeLists.txt`.
- `cmake/Find<BACKEND>.cmake` or equivalent package discovery.
- Unit-test config propagation and backend-specific test linkage.

## Agent Workflow

1. Read an existing backend in the same domain and mirror its structure.
2. Add the smallest supported routine first.
3. Build with unrelated default backends disabled when isolating the new backend.
4. Add tests before claiming integration is complete.
5. Document unsupported routines and target devices.

## Gotchas

- A compile-time dispatch path and runtime dispatch table are separate integration surfaces.
- Static and shared builds can require different link handling.
- Backend discovery must work from both CMake variables and environment variables where local convention supports it.
- Unit tests need compile definitions that reflect enabled backend options.
