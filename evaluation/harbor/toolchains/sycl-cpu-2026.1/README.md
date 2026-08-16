# SYCL hosted-CPU toolchain

This is the validated shared image for the opt-in `hosted-toolchain` tier. It installs the pinned Intel oneAPI DPC++/C++ 2026.1.1 compiler package on a pinned Ubuntu 24.04 amd64 base and deliberately excludes the full oneAPI toolkit.

The image build is also its first compatibility gate. It compiles and runs `smoke.cpp` on a real OpenCL CPU device, and `sycl-ls` must discover that device. A runner without a working CPU device will fail the build instead of silently entering the evaluator fleet.

The Intel compiler package contains the compiler, SYCL runtime, OpenCL CPU runtime, and their dependencies. Its stock environment initializer exposes only the common component in this minimal installation, so the image sets the installed compiler and runtime library paths explicitly. No additional oneAPI package is required.

Local validation is recorded in the [2026-08-16 activation report](../../results/2026-08-16-sycl-compile-link-activation.md). Rebuild it only in an opt-in job or after allocating the expected disk space:

```sh
docker build \
  --tag uxl-sycl-cpu:2026.1.1 \
  evaluation/harbor/toolchains/sycl-cpu-2026.1
```

Harbor tasks must consume the recorded immutable digest, not the mutable local tag. Record a new digest and rerun the gate whenever the base or compiler package changes. Reclaim the builder cache after those measurements if the build runs on a storage-constrained workstation.

The intended adoption order is:

1. Verify the OpenCL CPU smoke test on each hosted runner class used by the evaluator.
2. Calibrate the implemented `sycl-compile-time-backend-link` task with matched no-skill and skill arms.
3. Add only the oneMath CPU backend needed by `onemath-dispatch-overhead-benchmark`, preferably as a derived image.

The skill and task remain hardware-agnostic. The image has currently been verified on an Intel CPU; CI must route it only to a runner class where the OpenCL CPU gate passes. It must not assume that an arbitrary public runner exposes a compatible CPU runtime.
