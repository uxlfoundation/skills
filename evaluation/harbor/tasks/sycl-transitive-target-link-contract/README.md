# SYCL transitive target-link task

This executable task reproduces a target-graph failure. A CMake interface target supplies the SYCL compile and link requirements, and an object library consumes it privately. The SYCL object compiles, but the host pipeline embeds that object without propagating the link requirement to the final executable, which fails with unresolved `sycl::_V1` symbols.

The verifier protects all sources, the CMake helper module, and the reproducer. It rejects global flags and hardcoded oneAPI paths or library names, requires a target-scoped repair and diagnosis, proves that the final link command contains `-fsycl`, resolves `libsycl`, and runs one public plus four hidden cases on the explicitly selected OpenCL CPU.

The pinned 2026.1.1 toolchain image and Harbor task were activated on 2026-08-16 after the unchanged no-op arm scored `0` and the oracle scored `1` with zero exceptions. The task is hardware-agnostic but requires a runner with a compatible OpenCL CPU device.
