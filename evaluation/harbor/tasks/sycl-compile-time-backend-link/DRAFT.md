# Draft status

The task source, broken build, oracle repair, and verifier are prepared, but this directory deliberately has no active `task.toml`. The suite entry must remain `planned` until the pinned 2026.1 compiler image passes its Native CPU smoke test and Harbor records an unchanged baseline reward of `0` and oracle reward of `1`.

Development validation used the workstation's existing DPC++ 2023.2 installation and its real OpenCL CPU device. The untouched project configured and compiled its SYCL object, then failed at the host-only `g++` final link with unresolved SYCL symbols. The oracle linked through `icpx -fsycl`, loaded `libsycl`, executed on the selected CPU device, and passed four additional deterministic input cases.
