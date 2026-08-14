# Hosted-toolchain image selection: 2026-08-14

## Outcome

Use a compiler-only image built from the pinned Intel oneAPI DPC++/C++ 2026.1.1 package, rather than pulling the full oneAPI toolkit into the default evaluator environment. The bootstrap definition is in [`toolchains/sycl-cpu-2026.1`](../toolchains/sycl-cpu-2026.1/README.md). It uses a pinned Ubuntu 24.04 amd64 base and makes a DPC++ Native CPU compile-and-run probe a mandatory image-build step.

This preserves the design boundary: the two `hosted-toolchain` tasks exercise authentic compiler, linker, runtime, and backend behavior on a generic CPU. They do not make a target-device performance claim and they do not add a multi-gigabyte toolkit to every lightweight evaluation run.

## Options considered

| Option | Current status | Remote size evidence | Decision |
| --- | --- | ---: | --- |
| `intel/oneapi-toolkit:2026.1.0-devel-ubuntu24.04` | Current Intel verified-publisher image | 3.35 GB compressed | Reject for routine evaluator use; much broader than the two tasks need. |
| `intel/cpp-essentials` | Deprecated starting with oneAPI 2026.0 | About 2.4 GB compressed | Reject; smaller but no longer updated. |
| Pinned DPC++ compiler package on Ubuntu 24.04 | Current standalone Intel package | 0.897 GiB Intel package payload; 2.889 GiB installed before Ubuntu/build tools | Select for validation. |

The compiler-only totals were calculated from Intel's live APT `binary-amd64` and `binary-all` package indexes by recursively resolving the `intel-oneapi-dpcpp-cpp-2026.1=2026.1.1-325` dependency closure. They exclude Ubuntu base and build-tool packages. Intel's published compiler requirements independently describe approximately 3 GB as the minimum installation for the compiler and supporting libraries, which is consistent with this calculation.

## Hardware-agnostic execution gate

The [DPC++ Native CPU design](https://intel.github.io/llvm/design/SYCLNativeCPU.html) describes a CPU target with no dependency beyond DPC++ and supports `-fsycl-targets=native_cpu`. The bootstrap image therefore compiles and executes a small buffer kernel with `ONEAPI_DEVICE_SELECTOR=native_cpu:cpu`. This is a gate, not yet a result: the image has not been downloaded locally, so availability of the Native CPU target in Intel's packaged compiler remains to be demonstrated by a successful build.

## Reproducibility and storage controls

- The Ubuntu base is pinned to the current linux/amd64 manifest digest.
- The Intel compiler package is pinned to `2026.1.1-325`.
- A successful image must be published or recorded by immutable digest before Harbor uses it.
- The full toolkit, deprecated C++ Essentials image, and image build cache should not be retained in the local WSL evaluator environment.
- The toolchain suite remains opt-in or scheduled; it is not part of the lightweight default suite.

## Remaining gate

Run the bootstrap build once on an opt-in generic-CPU runner, record cold-build time and final expanded size, and pin the resulting digest. If Native CPU execution passes, implement `sycl-compile-time-backend-link` first. Only then derive a oneMath image with the narrowest authentic CPU backend needed for `onemath-dispatch-overhead-benchmark`.
