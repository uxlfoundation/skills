# UXL Intel GPU runner preparation report

- Assessment date: 2026-08-18
- Qualification class: `windows-wsl-intel-gpu-candidate`
- Current native-Linux evaluator compatibility: **Not qualified** for the `/dev/dri/renderD*` contract
- Windows/WSL conclusion: **Ready for a future, separate Windows/WSL lane**
- Runner registration: Not performed
- Evaluator execution: Not performed

## Relevant host facts

| Fact | Observed value |
|---|---|
| Host OS | Windows, 64-bit, build 26200 |
| CPU capacity | 28 logical processors |
| Memory | 31.8 GB physical RAM |
| Intel discrete GPU | Intel Arc B580 Graphics; PCI vendor/device `8086:E20B`; Windows driver `32.0.101.8974` |
| Intel integrated GPU | Intel UHD Graphics 770; PCI vendor/device `8086:A780`; Windows driver `32.0.101.7088` |
| WSL | `2.7.11.0`; WSL2 kernel `6.18.33.2-2`; x86_64 |
| WSL distribution | Ubuntu 24.04 LTS |
| WSL GPU path | `/dev/dxg`; no `/dev/dri/renderD*` contract |
| Host-WSL SYCL visibility | Level Zero exposes Intel Graphics `0xa780` |
| Pinned-container SYCL visibility | Level Zero exposes Intel Graphics `0xe20b` (Arc B580) and `0xa780` (UHD 770) |
| Python in WSL | `3.12.3`, with `venv` and `pip` |
| Git in WSL | `2.43.0` |
| Intel DPC++ compiler | `2026.1.1` |
| Docker Desktop | `4.87.0`, per-user WSL2 mode |
| Docker Engine | `29.7.2`, Linux/amd64 engine |
| Docker Compose | `v5.4.0` |
| Free disk after setup | 487.3 GB on Windows `C:`; WSL virtual filesystem reports 950 GB available |
| Outbound GitHub HTTPS | Available; no inbound port is required or opened |

## Qualification evidence

### WSL host

- The default Ubuntu user is a dedicated non-administrator account with a dedicated runner directory.
- The account belongs to the WSL `render` and `video` groups and can access `/dev/dxg`.
- `ONEAPI_DEVICE_SELECTOR=level_zero:gpu sycl-ls` selected Intel Graphics `0xa780`.
- The minimal SYCL program compiled with `icpx -fsycl`, selected Intel Graphics `0xa780`, printed `42`, and exited `0`.

### Docker and pinned Intel image

- Docker's Ubuntu WSL integration is enabled explicitly.
- Windows and Ubuntu Docker clients both reached Docker Engine `29.7.2`; Compose reported `v5.4.0`.
- The `hello-world` container completed successfully.
- Docker mapped `/dev/dxg` into a Linux container successfully.
- The exact image was pulled and retained:
  `intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c`.
- A Windows/WSL container must map both `/dev/dxg` and WSL's user-space DirectX libraries while preserving the image's existing library path. With that contract, `sycl-ls` enumerated both `0xe20b` and `0xa780`.
- Inside the pinned image, the minimal SYCL program selected Intel Graphics `0xe20b` (Arc B580), printed `42`, and exited `0`.

The validated Windows/WSL device-discovery shape, when run directly inside Ubuntu WSL, is:

```bash
docker run --rm \
  --device /dev/dxg:/dev/dxg \
  --mount type=bind,src=/usr/lib/wsl,dst=/usr/lib/wsl,readonly \
  -e ONEAPI_DEVICE_SELECTOR=level_zero:gpu \
  intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c \
  bash -lc 'export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${LD_LIBRARY_PATH}"; sycl-ls'
```

The same check is saved as `uxl-wsl-oneapi-device-check.sh` in this workspace and completed with exit code `0`.

This is **not** a substitute for the native-Linux command using `/dev/dri` and a render-node group ID. A future Windows/WSL Harbor task must encode this as its own container contract.

## Status

| Area | Status | Evidence or blocker | Next action |
|---|---|---|---|
| Host classification | Ready for proposed lane | `windows-wsl-intel-gpu-candidate`; WSL2 Ubuntu 24.04 is operational | Use only a separate Windows/WSL workflow |
| Intel GPU visibility | Pass for Windows/WSL | `/dev/dxg`; pinned image enumerated Arc B580 `0xe20b` and UHD 770 `0xa780` | Keep `/dev/dxg` contract distinct from `/dev/dri` |
| Docker/container GPU | Pass for Windows/WSL | Pinned-image SYCL smoke selected Arc B580, returned `42`, exit `0` | Encode `/dev/dxg`, `/usr/lib/wsl`, and library-path handling in the future task |
| Security isolation | Prepared | Dedicated non-admin WSL account/directory; Docker installed per-user; no inbound ports or runner service | Run the eventual runner interactively and only for reviewed jobs |
| Runner registration | Waiting | Private repo URL and one-time token intentionally absent | Wait for control repo |
| Evaluator task | Waiting | Reviewed evaluator commit is not yet published | Wait for commit/bundle |

## Changes made

- Enabled the Windows Subsystem for Linux and Virtual Machine Platform features and automatic hypervisor launch.
- Installed WSL `2.7.11.0` and Ubuntu 24.04 LTS.
- Created a dedicated non-administrator WSL account and runner directory.
- Installed Python 3.12, `venv`, `pip`, Git, Intel Level Zero/OpenCL runtimes, and Intel DPC++ compiler 2026.1.1.
- Installed Docker Desktop 4.87.0 in per-user WSL2 mode and enabled integration for Ubuntu 24.04.
- Pulled the exact pinned Intel oneAPI image and retained named stopped probe containers as evidence.
- Compiled and ran SYCL smoke tests on the WSL host and inside the pinned image.
- Opened no inbound firewall ports, changed no GPU drivers, registered no GitHub runner, configured no runner service, and ran no evaluator code.

## Remaining controlled gates

1. The existing evaluator task remains native-Linux-only and requires `/dev/dri/renderD*`; this Windows host must never be labeled compatible with that contract.
2. A future Windows/WSL task and workflow must use labels `uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab` and the validated `/dev/dxg` container contract above.
3. Runner registration requires the private control-repository URL and one-time registration token. The token must not be saved, logged, or added to this report.
4. The runner must initially run interactively, not as a service, and must not execute untrusted pull-request code.
5. Evaluator execution requires a reviewed commit SHA or bundle containing `sycl-device-discovery`; the stale public default branch must not be used silently.

## Qualification conclusion

This machine is **not qualified for the current native-Linux Intel GPU task**. It is fully prepared and qualified as a **Windows/WSL Intel GPU candidate** for a future separate lane: WSL2, Ubuntu, Python 3.12, Git, Docker/Compose, Intel runtimes, pinned-image device discovery, and an Arc B580 SYCL smoke test all pass.
