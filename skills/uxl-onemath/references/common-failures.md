# oneMath Common Failure Triage

Use this reference when a user gives an error but not enough context.

## `ONEMATH::SYCL::SYCL target was not found`

Likely causes:

- Compiler was not set during CMake configure.
- CMake cache still points to an older compiler or package root.
- SYCL compiler package is not discoverable.

Ask for:

- Configure command.
- `CMAKE_CXX_COMPILER`.
- CMake cache entries for oneMath and SYCL.
- Whether the project uses installed oneMath or FetchContent.

## Headers Conflict With Intel oneMKL

Likely causes:

- Installed oneMath headers are treated as system includes with lower priority.
- Intel oneMKL include paths appear earlier than expected.

Mitigations to check:

- CMake version and exported target behavior.
- `NO_SYSTEM_FROM_IMPORTED` for older CMake versions.
- Include ordering from generated build files.

## Backend Library Not Found At Runtime

Likely causes:

- Runtime dispatch linked but backend dynamic libraries are missing from loader paths.
- Third-party backend library is installed for link time but unavailable at run time.
- Device selector chooses a backend that was not deployed.

Ask for:

- Runtime error text.
- `PATH` on Windows or `LD_LIBRARY_PATH` on Linux.
- Enabled backend flags.
- Device selected at runtime.

## Wrong Numerical Result

Check before tuning:

- Matrix layout and leading dimensions.
- Batch strides and pointer mode.
- Queue/event dependencies.
- Precision and accumulation assumptions.
- Whether input/output buffers are read before asynchronous work completes.
