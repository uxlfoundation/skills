# SYCL generic-CPU toolchain

This is the candidate shared image for the opt-in `hosted-toolchain` tier. It installs the pinned Intel oneAPI DPC++/C++ 2026.1.1 compiler package on a pinned Ubuntu 24.04 amd64 base and deliberately excludes the full oneAPI toolkit.

The image build is also its first compatibility gate. It compiles and runs `smoke.cpp` through the DPC++ Native CPU target, which is intended to avoid dependence on an installed GPU or vendor-specific OpenCL device. A compiler distribution without a working Native CPU target will fail the build instead of silently entering the evaluator fleet.

No local build is part of image selection. Build it only in an opt-in job or after allocating the expected disk space:

```sh
docker build \
  --tag uxl-sycl-cpu:2026.1.1 \
  evaluation/harbor/toolchains/sycl-cpu-2026.1
```

After the first successful build, record the elapsed cold-build time, `docker image inspect` size, and immutable image digest. Harbor tasks must consume the resulting digest, not this mutable local tag. Reclaim the builder cache after those measurements if the build runs on a storage-constrained workstation.

The intended adoption order is:

1. Verify the Native CPU smoke test on a generic hosted CPU.
2. Implement `sycl-compile-time-backend-link` on the resulting digest.
3. Add only the oneMath CPU backend needed by `onemath-dispatch-overhead-benchmark`, preferably as a derived image.
