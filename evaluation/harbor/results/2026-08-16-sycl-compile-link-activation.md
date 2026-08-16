# SYCL compile/link task activation: 2026-08-16

## Outcome

`sycl-compile-time-backend-link` is implemented as the first opt-in `hosted-toolchain` task. It tests whether an agent can reproduce and repair a mixed-driver SYCL build: the SYCL object compiles with `icpx -fsycl`, while the unchanged host-only `g++` final link fails with unresolved `sycl::_V1` symbols. The oracle restores the SYCL link contract with `icpx -fsycl`, loads `libsycl`, and executes on a real CPU device.

## Toolchain gate

| Check | Result |
| --- | --- |
| Compiler | Intel oneAPI DPC++/C++ 2026.1.1 (`2026.1.1-325`) |
| Image ID | `sha256:90c67a1df80f57be32f0880ea5d638a75fd3df596ad2184e75d2a67c36513d79` |
| OCI image content (`docker image inspect .Size`) | 1,491,972,989 bytes |
| Uncompressed layer history | About 3.68 GB |
| Local Docker image-store listing | 5.17 GB |
| Cold provisioning to first smoke gate | 268.8 seconds |
| Corrected cached final build | 11.8 seconds |
| Device gate | Intel OpenCL CPU discovered by `sycl-ls` |
| Smoke kernel | Pass |

The packaged compiler accepts the Native CPU target flag but lacks the required Native CPU libspirv bitcode. Its OpenCL CPU runtime is complete, but the minimal package's stock environment initializer omits component runtime paths. The image explicitly exposes the compiler, SYCL, UMF, TBB, TCM, and common library locations and makes device discovery plus execution mandatory build gates.

## Discrimination

| Evaluation | Job | Reward | Exceptions | Evidence |
| --- | --- | ---: | ---: | --- |
| Unchanged no-op | `sycl-link-baseline-20260816-r1` | 0.000 | 0 | No repair or diagnosis artifact |
| Oracle, initial | `sycl-link-oracle-20260816-r1` | 0.000 | 0 | Exposed a verifier `pipefail`/SIGPIPE defect after successful execution |
| Oracle, schema audit | `sycl-link-oracle-20260816-r2` | excluded | 1 | Device-name list was invalid in Harbor's numeric reward schema |
| Oracle, final | `sycl-link-oracle-20260816-r3` | 1.000 | 0 | Public case plus four hidden cases; one real CPU device |

Direct execution separately confirms that the unchanged project reaches the intended final link and fails with unresolved `sycl::_V1` references. The verifier now captures `nm` and `ldd` output before matching it, avoiding false SIGPIPE failures under `set -o pipefail`; device names remain diagnostic stdout while numeric counts are stored in `reward.json`.

## Scope

The task evaluates hardware-agnostic build and triage behavior, not target-specific performance. Its infrastructure requires a compatible OpenCL CPU runtime and has been validated on the local Intel CPU runner. CI should dispatch it only to a runner class that passes the same device gate; it must not assume an arbitrary free public runner is compatible.

The skill still needs matched no-skill versus skill calibration. Until then, its portfolio calibration remains `uncalibrated`, even though the task implementation and oracle are valid.
