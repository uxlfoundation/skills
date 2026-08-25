# SYCL compile-time/backend link task

This executable task reproduces a mixed-toolchain build failure: `icpx -fsycl` correctly creates a SYCL object, but a host-only `g++` final link omits the SYCL link contract and fails with unresolved `sycl::_V1` symbols. The accepted repair links through the SYCL-capable driver and records the diagnosis.

The verifier protects the source and reproduction files, checks the diagnosis, rebuilds the repaired project, verifies its symbol and dynamic-library contracts, runs one public case plus four hidden cases, and requires execution on the explicitly selected OpenCL CPU device.

The pinned 2026.1.1 toolchain image and Harbor task were activated on 2026-08-16 after the unchanged no-op arm scored `0` and the oracle scored `1` with zero exceptions. The task behavior is hardware-agnostic; its evaluator environment requires a runner with a compatible OpenCL CPU device.
