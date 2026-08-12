---
name: uxl-onedpl
description: "Use for oneAPI DPC++ Library (oneDPL) work: C++ standard algorithm migration, host and device execution policies, SYCL queues and devices, iterator and data movement constraints, parallel STL behavior, backend selection through oneTBB/OpenMP/SYCL, CUDA or GPU device policy troubleshooting, and algorithm correctness/performance validation."
---

# UXL oneDPL

## Purpose

Help an agent apply oneDPL algorithms with the right execution policy, data location, iterator category, and SYCL dependency model.

## First Pass

1. Determine whether the work should run on host parallel policies or SYCL device policies.
2. Identify algorithm, iterator category, data ownership, memory model, queue/device selection, and required ordering.
3. Check current docs or releases for exact algorithm/device support and known issues before promising portability.
4. Read existing tests and CMake configuration for policy and backend conventions.

## Policy Selection

- Use host policies when data is on host and CPU parallelism is enough.
- Use device policies when the algorithm should run on a SYCL device and data movement is explicit or already managed.
- Construct policies from a known queue when the application already owns device selection and dependencies.
- Do not require a SYCL-capable device for host-only work unless the project configuration already does.

## Implementation Workflow

1. Preserve the serial or standard-library contract first, including stability, ordering, and exception expectations.
2. Make data location and lifetime explicit: host memory, USM, buffers, or project wrapper types.
3. Select includes and namespaces from the current oneDPL docs.
4. Add a small correctness test that compares against serial `std` behavior.
5. Add device-specific tests only when a suitable SYCL device exists in CI or the user's environment.
6. Benchmark after correctness, with data transfer and queue synchronization costs stated.

## Gotchas

- Device algorithms can fail for unsupported iterator categories or data access patterns.
- Asynchronous device work must be synchronized before reading results on host.
- Stable ordering is not guaranteed unless the chosen algorithm promises it.
- Device lambda restrictions differ from ordinary host C++ lambdas.
- A tiny range can be slower on a device once transfer and launch overhead are included.

## Output Contract

When delivering oneDPL work, include:

- Algorithm and execution policy.
- Data location, iterator constraints, and queue ownership.
- Synchronization points.
- Serial/reference correctness test.
- Device and backend assumptions.

## References

Read [official sources](references/official-sources.md) for execution policies, device policy construction, and current release notes.
