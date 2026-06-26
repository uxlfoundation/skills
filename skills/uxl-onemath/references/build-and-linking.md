# oneMath Build and Linking

Use this reference for compiler, CMake, backend, and runtime loader issues.

Source anchors:

- Selecting a compiler: https://uxlfoundation.github.io/oneMath/selecting_a_compiler.html
- Building with DPC++: https://uxlfoundation.github.io/oneMath/building_the_project_with_dpcpp.html
- Building with AdaptiveCpp: https://uxlfoundation.github.io/oneMath/building_the_project_with_adaptivecpp.html
- Using oneMath with CMake: https://uxlfoundation.github.io/oneMath/using_onemath_with_cmake.html

## Compiler Choice

From current oneMath docs:

- Intel GPU requires Intel oneAPI DPC++ compiler: `icpx` on Linux or `icx` on Windows.
- Linux NVIDIA GPU requires a oneAPI DPC++ `clang++` built with CUDA support or AdaptiveCpp, except where the docs exclude domains such as LAPACK or DFT for AdaptiveCpp.
- Linux AMD GPU requires oneAPI DPC++ `clang++` with HIP support or AdaptiveCpp.
- CPU-only or non-discrete-GPU work can use Intel DPC++, open DPC++, AdaptiveCpp on Linux, and Intel DPC++ or `clang-cl` on Windows.

Always re-check the current compiler page before making exact backend/compiler claims.

## CMake Consumption

For an installed oneMath:

- Use `find_package(oneMath REQUIRED)`.
- Link `ONEMATH::onemath` for the whole runtime-dispatch library.
- Link `ONEMATH::onemath_<domain>_<backend>` for compile-time dispatch against a specific backend.
- The compiler used by the consuming target should match the compiler used to build oneMath.

## Backend Build Flags

Common DPC++ build options include:

- Intel oneMKL CPU/GPU: `ENABLE_MKLCPU_BACKEND`, `ENABLE_MKLGPU_BACKEND`.
- CUDA: `ENABLE_CUBLAS_BACKEND`, `ENABLE_CUSOLVER_BACKEND`, `ENABLE_CURAND_BACKEND`, `ENABLE_CUFFT_BACKEND`, `ENABLE_CUSPARSE_BACKEND`.
- ROCm: `ENABLE_ROCBLAS_BACKEND`, `ENABLE_ROCSOLVER_BACKEND`, `ENABLE_ROCRAND_BACKEND`, `ENABLE_ROCFFT_BACKEND`, `ENABLE_ROCSPARSE_BACKEND`.
- CPU libraries: `ENABLE_NETLIB_BACKEND`, `ENABLE_ARMPL_BACKEND`, `ENABLE_ARMPL_OPENRNG`.

For ROCm DPC++ builds, check whether `HIP_TARGETS` is required for the target GPU architecture.

## Triage Checklist

When oneMath cannot be found or linked:

1. Inspect `CMAKE_CXX_COMPILER`, `oneMath_ROOT`, `CMAKE_PREFIX_PATH`, and the CMake cache.
2. Confirm runtime dispatch versus compile-time dispatch.
3. Confirm the selected target exists in the installed oneMath package.
4. Confirm third-party backend libraries are installed and discoverable.
5. Confirm runtime loader paths, not only link paths.
6. Use `uxl-sycl-build-debug` when compiler/device discovery is unclear.
