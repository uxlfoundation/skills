# Hosted-toolchain image selection: 2026-08-14

## Outcome

Use a compiler-only image built from the pinned Intel oneAPI DPC++/C++ 2026.1.1 package, rather than pulling the full oneAPI toolkit into the default evaluator environment. The bootstrap definition is in [`toolchains/sycl-cpu-2026.1`](../toolchains/sycl-cpu-2026.1/README.md). It uses a pinned Ubuntu 24.04 amd64 base and makes an OpenCL CPU compile-and-run probe a mandatory image-build step.

This preserves the design boundary: the two `hosted-toolchain` tasks exercise authentic compiler, linker, runtime, and backend behavior on a generic CPU. They do not make a target-device performance claim and they do not add a multi-gigabyte toolkit to every lightweight evaluation run.

## Options considered

| Option | Current status | Remote size evidence | Decision |
| --- | --- | ---: | --- |
| `intel/oneapi-toolkit:2026.1.0-devel-ubuntu24.04` | Current Intel verified-publisher image | 3.35 GB compressed | Reject for routine evaluator use; much broader than the two tasks need. |
| `intel/cpp-essentials` | Deprecated starting with oneAPI 2026.0 | About 2.4 GB compressed | Reject; smaller but no longer updated. |
| Pinned DPC++ compiler package on Ubuntu 24.04 | Current standalone Intel package | 0.897 GiB Intel package payload; 2.889 GiB installed before Ubuntu/build tools | Select for validation. |

The compiler-only totals were calculated from Intel's live APT `binary-amd64` and `binary-all` package indexes by recursively resolving the `intel-oneapi-dpcpp-cpp-2026.1=2026.1.1-325` dependency closure. They exclude Ubuntu base and build-tool packages. Intel's published compiler requirements independently describe approximately 3 GB as the minimum installation for the compiler and supporting libraries, which is consistent with this calculation.

## Hardware-agnostic execution gate

The initial design selected the [DPC++ Native CPU target](https://intel.github.io/llvm/design/SYCLNativeCPU.html). Empirical validation found that Intel's 2026.1.1 binary compiler accepts `-fsycl-targets=native_cpu` but does not ship the required Native CPU libspirv bitcode. Disabling that bitcode is not a viable fallback because the final link retains unresolved SPIR-V built-ins.

The same minimal package does ship a working Intel OpenCL CPU runtime. Its stock environment initializer omits compiler-component runtime paths in this installation, so the image supplies explicit compiler, UMF, TBB, and TCM library paths. With those paths, `sycl-ls` discovers the host CPU and the buffer kernel executes successfully. This keeps the task hardware-agnostic, but makes a working OpenCL CPU device an explicit runner capability.

## Reproducibility and storage controls

- The Ubuntu base is pinned to the current linux/amd64 manifest digest.
- The Intel compiler package is pinned to `2026.1.1-325`.
- A successful image must be published or recorded by immutable digest before Harbor uses it.
- The full toolkit, deprecated C++ Essentials image, and image build cache should not be retained in the local WSL evaluator environment.
- The toolchain suite remains opt-in or scheduled; it is not part of the lightweight default suite.

## Validation result

The cold compiler provisioning reached its first smoke gate in 268.8 seconds. After correcting the environment and replacing the unavailable Native CPU target with the packaged OpenCL CPU runtime, the cached final build completed in 11.8 seconds. The final image reports 1,491,972,989 bytes through `docker image inspect` and has local immutable identifier `sha256:90c67a1df80f57be32f0880ea5d638a75fd3df596ad2184e75d2a67c36513d79`.

`sycl-compile-time-backend-link` was activated on this image on 2026-08-16. Harbor recorded the unchanged no-op arm at reward `0` and the oracle at reward `1` with four hidden cases, one real OpenCL CPU device, and zero exceptions. The remaining hosted-toolchain work is the separate oneMath backend task.
