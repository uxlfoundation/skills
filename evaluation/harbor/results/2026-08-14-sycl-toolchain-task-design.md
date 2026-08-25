# SYCL compile/link evaluator design: 2026-08-14

## Objective

`sycl-compile-time-backend-link` will be the first executable task in the opt-in `hosted-toolchain` tier. It tests whether an agent can preserve the first failure, distinguish compilation from linking and runtime discovery, repair the build reproducibly, and prove a deterministic SYCL result without requiring a GPU.

This task is intentionally distinct from `sycl-cmake-compiler-cache`. The existing task grades a written diagnosis of stale configure state. The new task requires an actual source/build repair and rejects an answer that only describes the right idea.

## Constructed failure

The public project compiles a SYCL translation unit with `icpx -fsycl -fsycl-targets=native_cpu`, then incorrectly links the object through the host `g++` driver without the SYCL link step. The object is produced, but the final link fails with unresolved SYCL runtime and offload-wrapper symbols. The task narrative reports this as a possible missing backend installation and asks the agent to diagnose the phase before changing packages.

The expected repair moves compiler selection and the Native CPU target into a clean, reproducible CMake configuration. Compilation and final linking must use the compatible DPC++ driver and flags. The repaired program then executes a deterministic kernel with `ONEAPI_DEVICE_SELECTOR=native_cpu:cpu`, prints the selected backend/device, and validates its output.

## Evaluation contract

| Gate | Verifier evidence | Failure prevented |
| --- | --- | --- |
| Reproduce | Original object exists; untouched project fails at the link command, not compile or runtime | Misclassifying the first failure |
| Repair | Clean configure and verbose build succeed with the pinned DPC++ toolchain | Session-only flags and stale build-tree fixes |
| Link | Final link uses the SYCL-capable driver and includes the Native CPU target | Compiling with SYCL but linking as ordinary host C++ |
| Execute | Explicit Native CPU selector runs the kernel and validates a held-out result | Treating build success as runtime proof |
| Diagnose | Short artifact names the link phase, incompatible link driver, and any unverified target-device claims | Correct patch with unsupported explanation |

The hidden verifier will rebuild from a clean directory, add a second SYCL translation unit, and change the input size and values. It will inspect build commands and observable program results rather than require one exact CMake implementation. Protected reproduction and verifier files will prevent an agent from replacing the test with a constant-output script.

## Promotion sequence

1. Build the shared compiler-only image and pass its Native CPU smoke gate.
2. Materialize this task against the immutable image digest.
3. Run unchanged baseline and oracle repairs; require baseline reward `0` and oracle reward `1`.
4. Audit the verifier with at least one alternate correct CMake repair and one plausible shortcut.
5. Run three attempts for no skill, previous skill, and candidate skill; record verified quality, errors, runtime, cost, and total tokens per verified success.
6. Promote only if the task is discriminating and the current skill does not create an unacceptable quality or efficiency regression.

Until steps 1–3 pass, the suite entry remains planned and uncalibrated.

## Development validation

The complete task was initially staged under [`tasks/sycl-compile-time-backend-link`](../tasks/sycl-compile-time-backend-link/README.md) without an active `task.toml`. It was exercised against the workstation's pre-existing DPC++ 2023.2 toolchain and Intel OpenCL CPU device. The untouched build successfully produced the SYCL object and then failed at the `g++` final link with unresolved `sycl::_V1` symbols. The oracle used `icpx -fsycl` for the final link, resolved `libsycl.so.6`, executed the kernel on the explicitly selected CPU device, and matched the complete checksum for the public case plus four additional input cases.

This validated the constructed failure and repair shape before the required Harbor baseline/oracle run on the pinned 2026.1 image. The final image uses its packaged OpenCL CPU runtime because the binary compiler package does not include the Native CPU libspirv payload.
