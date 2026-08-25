# Codex handoff: prepare a personal Intel GPU machine as a UXL Skills Evaluator runner

Copy everything below the separator into Codex on the personal Intel GPU machine.

---

I want to prepare this personal computer as a controlled, manually enabled runner for the UXL skills evaluator. Work autonomously through the safe preparation and qualification steps below, and leave me with a concise status table and a machine-readable-enough Markdown report.

## Target evaluator contract

The evaluator repository is public at [uxlfoundation/skills](https://github.com/uxlfoundation/skills), but the evaluator changes needed for the Intel GPU task have **not been pushed yet**. Do not assume the current public branch contains the final task. Prepare and qualify the host now; execution of the exact Harbor task will happen after I provide a reviewed commit SHA or bundle.

The existing hardware task and GitHub Actions workflow target:

- a Linux x64 host;
- an Intel GPU exposed as `/dev/dri/renderD*`;
- Docker Engine with Compose v2;
- Harbor `0.20.0` with Python `3.12`;
- the container image `intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c`;
- GitHub runner labels `uxl,sycl,gpu,intel-gpu` in addition to the automatic `self-hosted,linux,x64` labels;
- the Harbor task `sycl-device-discovery`.

Windows/WSL exposing an Intel GPU through `/dev/dxg` is a useful but different execution contract. It must not be labeled or reported as compatible with the current native-Linux `/dev/dri` task. If this is a Windows machine, prepare and report it as a proposed Windows/WSL lane and stop short of claiming evaluator qualification.

## Safety boundaries

1. Do not open inbound firewall ports and do not expose SSH, RDP, Docker, or a web service to the public internet. A GitHub Actions runner makes an outbound HTTPS connection; it needs no inbound port.
2. Do not register this machine as a runner in the public `uxlfoundation/skills` repository.
3. The eventual runner belongs in a **private control repository**, runs only reviewed manual or scheduled workflows, and checks out the public evaluator at an explicit commit SHA.
4. Do not register the runner until I provide the private repository URL and a one-time GitHub registration token. Never save, echo, log, or include that token in the report.
5. Do not print secrets, private SSH keys, credential stores, complete environment-variable dumps, or unrelated personal files.
6. Do not run untrusted pull-request code. Self-hosted jobs can access host files and credentials available to the runner account.
7. Prefer a dedicated, non-administrator OS account and dedicated working directory. Recommend one if absent. Ask before creating an account, making administrator-level installations, changing GPU drivers, enabling WSL features, or rebooting/signing out.
8. Do not install a new operating system or configure dual boot. If native Linux is required, report that as a next action.
9. Initially run the GitHub runner interactively, not as a persistent service, so I explicitly control when it is online.
10. Preserve evidence. Do not delete runner workspaces or Docker data without my explicit approval.

## Phase A: inspect the machine

First determine whether the host is native Linux or Windows. Use read-only commands before proposing changes.

On native Linux, collect:

```bash
uname -a
cat /etc/os-release
lscpu
lspci -nnk | grep -A3 -Ei 'vga|display'
ls -l /dev/dri 2>/dev/null || true
find /dev/dri -maxdepth 1 -name 'renderD*' -ls 2>/dev/null || true
id
python3 --version || true
git --version || true
docker version || true
docker compose version || true
df -h .
```

On Windows, collect from PowerShell:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, PNPDeviceID
wsl --status
wsl --list --verbose
git --version
py -0p
docker version
docker compose version
Get-PSDrive -PSProvider FileSystem
```

If WSL is installed, inspect it without treating `/dev/dxg` as `/dev/dri`:

```powershell
wsl -- bash -lc 'uname -a; cat /etc/os-release; id; ls -l /dev/dxg /dev/dri 2>/dev/null || true; python3 --version || true; git --version || true'
```

Classify the machine as exactly one of:

- `native-linux-intel-gpu-candidate`
- `windows-wsl-intel-gpu-candidate`
- `not-ready-no-intel-gpu-visible`
- `blocked-prerequisite`

Create `uxl-runner-prep-report.md` in the current workspace. Record only relevant system facts: OS, CPU architecture, Intel GPU name and PCI/PNP ID, driver/kernel information, GPU device path, Docker and Compose versions, Python and Git versions, free disk, current qualification class, changes made, blockers, and next steps. Do not record usernames, tokens, external IP addresses, or unrelated hardware identifiers.

## Phase B: prepare prerequisites

Aim for at least 4 CPU threads, 16 GB RAM, and 40 GB free disk. Report shortfalls rather than deleting files.

### Native Linux path

The goal is Docker Engine with Compose v2, Python 3.12 or a compatible isolated environment, Git, the Intel host driver/runtime, and `/dev/dri/renderD*`.

If packages or driver changes are needed, explain the exact proposed commands and ask once before using `sudo` or changing system state. Use the distribution's official supported installation path. Do not replace a working GPU driver merely to obtain a newer version.

If the current user lacks the required access, propose:

```bash
sudo usermod -aG docker,render,video "$USER"
```

Explain that a fresh login is needed. Do not work around permission failures with a privileged container or world-writable device nodes.

### Windows/WSL path

The immediate goal is a readiness report for a distinct Windows/WSL lane. Check whether WSL2, an Ubuntu distribution, Docker Desktop with WSL integration, and the Intel Windows GPU driver are present. Ask before enabling Windows features, installing software, updating a driver, signing out, or rebooting.

Inside WSL, determine whether `/dev/dxg` exists and whether any installed SYCL tools can enumerate the Intel GPU. Do not fabricate `/dev/dri`, relabel the host as Linux, or modify the existing Linux-only workflow to force a match. Report what a future Windows/WSL Harbor task would need.

## Phase C: qualify native Linux container access

Run this phase only when native Linux exposes at least one `/dev/dri/renderD*` node and Docker works. Determine the render-node group ID and run the exact pinned container:

```bash
export INTEL_RENDER_GID="$(stat -c '%g' "$(find /dev/dri -maxdepth 1 -name 'renderD*' -print -quit)")"

docker run --rm \
  --device /dev/dri:/dev/dri \
  --group-add "$INTEL_RENDER_GID" \
  intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c \
  bash -lc 'ONEAPI_DEVICE_SELECTOR=level_zero:gpu sycl-ls'
```

Capture the relevant `sycl-ls` device description and command exit status in the report. If the GPU is absent, distinguish among host-driver, Level Zero runtime, Docker device mapping, and group-permission problems. Treat this as infrastructure failure—not a skill or evaluator failure.

If practical, also compile and run this minimal SYCL smoke program inside the same pinned image, with `ONEAPI_DEVICE_SELECTOR=level_zero:gpu`, and record the selected device plus correct result:

```cpp
#include <sycl/sycl.hpp>
#include <iostream>

int main() {
  sycl::queue q;
  int result = 0;
  {
    sycl::buffer<int> b(&result, sycl::range<1>(1));
    q.submit([&](sycl::handler& h) {
      auto out = b.get_access<sycl::access::mode::write>(h);
      h.single_task([=]() { out[0] = 42; });
    });
  }
  std::cout << q.get_device().get_info<sycl::info::device::name>() << "\n";
  std::cout << result << "\n";
  return result == 42 ? 0 : 1;
}
```

Use a temporary directory and do not modify system toolchains for this smoke test.

## Phase D: stage—but do not register—the GitHub runner

Do not guess the current GitHub Actions runner version or download URL. When the private control repository exists, its **Settings → Actions → Runners → New self-hosted runner** page will provide the current platform-specific download and checksum commands plus a one-time token.

For now:

1. Recommend a dedicated standard account and a dedicated runner directory.
2. Confirm outbound HTTPS to GitHub is available without opening inbound ports.
3. Recommend these custom labels for native Linux: `uxl,sycl,gpu,intel-gpu,personal-lab`.
4. Recommend these labels for a future Windows/WSL lane: `uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab`. It must use a separate workflow and task contract.
5. Do not configure the runner as a service.
6. Stop and request the private control-repository URL and one-time registration token before registration.

The eventual native-Linux registration command will have this shape, but use the exact command generated by GitHub:

```bash
./config.sh \
  --url '<private-control-repository-url>' \
  --token '<one-time-registration-token>' \
  --labels 'uxl,sycl,gpu,intel-gpu,personal-lab' \
  --ephemeral

./run.sh
```

Never paste the real token into a report or shell-history-generating helper script. Ephemeral registration means one job per registration; it does not automatically erase files left in the work directory.

## Phase E: exact evaluator run after the reviewed code is available

Do not run this phase yet unless I provide a repository checkout containing the task and a reviewed commit SHA. Do not silently use the stale public default branch.

On qualified native Linux, the eventual commands from that checkout are:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install harbor==0.20.0

export HARBOR_TELEMETRY=off
export INTEL_RENDER_GID="$(stat -c '%g' "$(find /dev/dri -maxdepth 1 -name 'renderD*' -print -quit)")"
export INTEL_VIDEO_GID="$(stat -c '%g' "$(find /dev/dri -maxdepth 1 -name 'card*' -print -quit)")"

harbor run \
  --path evaluation/harbor/tasks \
  --agent oracle \
  --include-task-name sycl-device-discovery \
  --job-name uxl-sycl-intel-gpu-oracle \
  --jobs-dir harbor-jobs \
  --n-concurrent 1 \
  --yes

python scripts/check_harbor_job.py \
  harbor-jobs/uxl-sycl-intel-gpu-oracle/result.json \
  --expected-trials 1 \
  --reward-floor 1.0
```

The oracle must pass before any model/skill comparison is attempted.

## Final response format

At the end, give me a concise table:

| Area | Status | Evidence or blocker | Next action |
|---|---|---|---|
| Host classification | ... | ... | ... |
| Intel GPU visibility | ... | ... | ... |
| Docker/container GPU | ... | ... | ... |
| Security isolation | ... | ... | ... |
| Runner registration | Waiting | Private repo URL and one-time token intentionally absent | Wait for control repo |
| Evaluator task | Waiting | Reviewed evaluator commit is not yet published | Wait for commit/bundle |

Also link the completed `uxl-runner-prep-report.md`. Clearly state whether the machine is qualified for the current native-Linux task, only ready for a future Windows/WSL lane, or blocked.
