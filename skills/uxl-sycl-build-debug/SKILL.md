---
name: uxl-sycl-build-debug
description: "Use for cross-UXL SYCL build and runtime troubleshooting: oneAPI DPC++ or AdaptiveCpp compiler selection, CMake configuration, target backends for Intel/NVIDIA/AMD devices, missing headers or libraries, link failures, runtime loader paths, device discovery, queue selector errors, plugin/runtime mismatches, and reproducible environment reports."
---

# UXL SYCL Build Debug

## Purpose

Help an agent separate compiler, CMake, linker, runtime loader, and device-selection failures for UXL projects that use SYCL.

## First Pass

1. Capture OS, shell, compiler command, CMake configure line, target hardware, installed backend runtimes, and the first failing error.
2. Run or ask the user to run `scripts/sycl_probe.py` when local environment evidence is useful.
3. Decide whether the failure is configure-time, compile-time, link-time, runtime loading, or device selection.
4. For current version or backend support claims, check the relevant project docs first.

## Triage Map

- Configure failure: inspect `CMAKE_CXX_COMPILER`, compiler identity, package roots, and cache values.
- Compile failure: inspect include paths, language standard, SYCL flags, target backend flags, and unsupported device code.
- Link failure: inspect selected dispatch mode, backend wrapper libraries, third-party math/communication libraries, and runtime search paths.
- Runtime load failure: inspect PATH/LD_LIBRARY_PATH, plugin paths, installed drivers, and dynamic backend availability.
- Device failure: inspect `sycl-ls` output, queue selector, backend-specific device filters, and driver/runtime versions.

## Workflow

1. Preserve the original error and command before changing flags.
2. Build a minimal SYCL smoke test or run the project's smallest example.
3. Change one variable at a time: compiler, backend target, package root, library path, or device filter.
4. Verify both build and runtime device discovery.
5. Write the fix as a reproducible command or CMake preset, not as session-only shell state.

## Gotchas

- `icpx`, open-source DPC++, and AdaptiveCpp are not interchangeable in flags, target support, or package discovery.
- A successful compile does not prove the backend runtime or device driver can load.
- `find_package` failures often come from CMake cache state; inspect the cache before adding new hints.
- GPU examples may silently select a CPU if the queue selector is too broad.
- Runtime dispatch libraries must be findable at execution time, not only at link time.

## Output Contract

When delivering a build/debug answer, include:

- Failing phase and root-cause hypothesis.
- Minimal reproduction command.
- Exact compiler/CMake/environment changes.
- Device/runtime validation command.
- What remains unverified.

## References

Read [official sources](references/official-sources.md) for compiler selection and project-specific backend setup.
