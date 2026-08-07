A SYCL application builds successfully but cannot find the expected GPU at runtime.

Run `/app/sycl_probe.py` and save its complete JSON output to `/app/sycl-probe.json`. Diagnose the device-discovery problem in `/app/diagnosis.md`, clearly separating build success from runtime availability. Include the observed `sycl-ls` evidence, relevant driver and runtime-path checks, device-filter checks, and a minimal smoke-test plan.
