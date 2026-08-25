# Handoff: qualified Windows/WSL Intel GPU evaluator runner

## Executive summary

This personal machine is prepared and qualified as a `windows-wsl-intel-gpu-candidate` for a **new, separate Windows/WSL evaluator lane**. Native Linux is not required and should not be proposed for this host.

The exact pinned Intel oneAPI container enumerated both Intel GPUs through WSL GPU paravirtualization, and a compiled SYCL smoke program selected the Arc B580, printed `42`, and exited `0`.

This host must **not** be routed to the existing native-Linux `/dev/dri/renderD*` task. The WSL contract uses `/dev/dxg` and a read-only mount of WSL's DirectX user-space libraries.

## Machine qualification

| Area | Result |
|---|---|
| Qualification class | `windows-wsl-intel-gpu-candidate` |
| Host | Windows x64, build 26200 |
| WSL | `2.7.11.0`, WSL2 kernel `6.18.33.2-2` |
| Distribution | Ubuntu 24.04 LTS, x86_64 |
| GPU device interface | `/dev/dxg` |
| Discrete GPU | Intel Arc B580, device ID `0xe20b` |
| Integrated GPU | Intel UHD Graphics 770, device ID `0xa780` |
| Docker Desktop | `4.87.0`, per-user WSL2 mode |
| Docker Engine | `29.7.2`, Linux/amd64 |
| Docker Compose | `v5.4.0` |
| Python in WSL | `3.12.3`, with `venv` and `pip` |
| Git in WSL | `2.43.0` |
| Host DPC++ compiler | `2026.1.1` |
| Dedicated execution identity | Non-administrator WSL account with a dedicated runner directory |

## Validated container contract

Pinned image:

```text
intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c
```

Validated device-discovery command, run directly inside Ubuntu WSL:

```bash
docker run --rm \
  --device /dev/dxg:/dev/dxg \
  --mount type=bind,src=/usr/lib/wsl,dst=/usr/lib/wsl,readonly \
  -e ONEAPI_DEVICE_SELECTOR=level_zero:gpu \
  intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c \
  bash -lc 'export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${LD_LIBRARY_PATH}"; sycl-ls'
```

Observed output:

```text
[level_zero:gpu] Intel(R) oneAPI Unified Runtime over Level-Zero V2, Intel(R) Graphics [0xe20b] 20.1.0 [1.15.38308+4]
[level_zero:gpu] Intel(R) oneAPI Unified Runtime over Level-Zero V2, Intel(R) Graphics [0xa780] 12.2.0 [1.15.38308+4]
```

Critical implementation details:

1. Map `/dev/dxg`; do not look for or fabricate `/dev/dri`.
2. Read-only mount `/usr/lib/wsl` at the same container path.
3. **Prepend** `/usr/lib/wsl/lib` to the image's existing `LD_LIBRARY_PATH`. Do not replace the existing value; doing so hides oneAPI libraries such as `libumf.so.1` and `libsycl.so.9`.
4. Set `ONEAPI_DEVICE_SELECTOR=level_zero:gpu`.
5. The render-node and video-node GID logic from native Linux does not apply.

Mapping only `/dev/dxg` was insufficient: the device appeared in the container, but `sycl-ls` reported no platforms until the WSL libraries and preserved library path were supplied.

## SYCL execution proof

The minimal program in `uxl-sycl-smoke.cpp` was compiled and run inside the pinned image using the contract above.

Observed output:

```text
Intel(R) Graphics [0xe20b]
42
```

Exit status: `0`.

The same program also passed directly in Ubuntu WSL, selecting device `0xa780` and returning `42`. The pinned container's newer runtime enumerated both devices and selected the Arc B580.

## Required broader-project changes

Create a distinct Windows/WSL Harbor task and workflow rather than broadening the existing native-Linux task.

Recommended custom runner labels:

```text
uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab
```

The workflow must require `windows-wsl` so this host cannot accidentally receive the native `/dev/dri` job. A runner launched inside WSL may still receive GitHub's automatic `self-hosted,linux,x64` labels; the custom `windows-wsl` label is the decisive lane discriminator.

The new task should:

- validate that `/dev/dxg` exists;
- use the exact pinned image digest;
- apply the validated `/dev/dxg` and `/usr/lib/wsl` mounts;
- preserve and prepend the image library path as shown above;
- require at least one `level_zero:gpu` device;
- compile and run a minimal SYCL workload, verifying both device selection and result `42`;
- treat missing GPU enumeration as infrastructure failure rather than skill failure;
- avoid native-Linux render/video group-ID assumptions;
- remain separate from `sycl-device-discovery` unless that task is explicitly refactored into OS-specific variants.

Suggested task name:

```text
sycl-device-discovery-windows-wsl
```

The oracle for this new task must pass before any model or skill comparison is attempted.

## Security and runner-control requirements

- Use a private control repository for runner registration and workflow dispatch.
- Permit only reviewed manual or scheduled workflows.
- Check out the public evaluator repository at an explicit reviewed commit SHA.
- Do not execute untrusted pull-request code.
- Keep the runner interactive initially; do not configure it as a service.
- Open no inbound firewall ports. The runner needs outbound HTTPS only.
- Never persist or log the one-time GitHub registration token.
- Retain the `windows-wsl` custom label permanently for this machine.

## Deliberately not completed

- GitHub Actions runner registration: waiting for a private control-repository URL and one-time registration token.
- Harbor evaluator execution: waiting for a reviewed commit SHA or bundle containing the Windows/WSL task.
- Harbor `0.20.0` environment: not created yet because the reviewed evaluator checkout is not available.
- Native-Linux qualification: not applicable and not required for this machine.

## Artifacts in the preparation workspace

- `uxl-runner-prep-report.md` — complete host report and status table.
- `uxl-wsl-oneapi-device-check.sh` — reproducible pinned-image discovery check; verified exit `0`.
- `uxl-sycl-smoke.cpp` — minimal SYCL smoke program.
- `uxl-runner-post-reboot.log` — sanitized preparation evidence.

## Requested response from the broader-project session

Return one of the following to this machine-preparation session:

1. A reviewed commit SHA containing the separate Windows/WSL Harbor task and workflow, or
2. A reviewed Git bundle/patch containing those changes plus the intended base commit.

If runner registration is desired afterward, separately provide the private control-repository URL and a fresh one-time registration token through a secure interactive channel. Do not place the token in a handoff document, repository, script, or chat transcript intended for retention.
