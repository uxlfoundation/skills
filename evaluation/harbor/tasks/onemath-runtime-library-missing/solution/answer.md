The successful `ONEMATH::onemath` link only confirms that the runtime dispatch front end was found. It does not prove that the selected CUDA backend is available at runtime.

First capture the selected SYCL device and confirm that it is the intended NVIDIA GPU. Then inspect which oneMath backend dynamic libraries were built and installed, confirm CUDA backend enablement, and use the platform loader diagnostics to see which dynamic library is missing. Check `LD_LIBRARY_PATH`, the executable's rpath/runpath, the oneMath installation prefix, and the CUDA runtime library locations.

Reproduce with a minimal GEMM, record `sycl-ls`, loader output, and the resolved shared libraries, then compare a CPU run with the GPU run. Treat device discovery, backend loading, and numerical correctness as separate checks.
