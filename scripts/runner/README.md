# Runner qualification helpers

These scripts support the Windows/WSL Intel GPU qualification packet in [`docs/runner/`](../../docs/runner/README.md).

- `uxl-runner-post-reboot.ps1` installs and configures WSL, Intel GPU/oneAPI packages, and Docker prerequisites, then records qualification evidence.
- `uxl-wsl-oneapi-device-check.sh` probes the pinned oneAPI container and device path.
- `uxl-sycl-smoke.cpp` is the minimal SYCL compile-and-run check used by the qualification workflow.

`uxl-runner-post-reboot.ps1` makes material host changes. Review it before use and run it only on a machine intentionally dedicated to this runner-preparation workflow. Its transcript is generated beside the script and should be moved to the workspace-level `artifacts/` directory after review rather than committed.
