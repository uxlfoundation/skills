# SYCL task draft and WSL reclaim: 2026-08-14

## Evaluator progress

The complete `sycl-compile-time-backend-link` task is drafted but deliberately remains planned. Development testing used the workstation's existing Intel oneAPI DPC++ 2023.2 installation and real OpenCL CPU device:

- The untouched project configured successfully.
- `icpx -fsycl` produced the SYCL object.
- The host-only `g++` final link failed with unresolved `sycl::_V1` symbols, establishing the intended link-phase baseline.
- The oracle used `icpx -fsycl` for the final link, resolved `libsycl.so.6`, executed on the explicitly selected CPU device, and passed the public input plus four additional input cases.

The draft has no active `task.toml`; it will not count as implemented until the pinned DPC++ 2026.1 image passes Native CPU execution and Harbor records unchanged baseline/oracle discrimination.

## Storage reclaim

After development validation, the obsolete package-managed oneAPI 2023.2 installation was removed from Ubuntu. The package manager reported 14.8 GB freed, Ubuntu filesystem usage fell from approximately 32 GiB to 18 GiB, and no `intel-oneapi-*` packages remain installed. User repositories and the unrelated Anaconda installation were not changed.

The Ubuntu filesystem was trimmed and WSL was shut down. Windows physical free space did not increase because offline VHD compaction requires administrator rights and this session is not elevated. The unsafe sparse-VHD override was not enabled. A later administrator session should compact only:

`C:\Users\jmelonak\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_79rhkp1fndgsc\LocalState\ext4.vhdx`

Until that compaction completes, the 2026.1 Docker image build remains paused because C: has less than 1 GiB physically free.
