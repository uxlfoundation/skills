# Intel GPU Runner Setup

Use controlled hardware only when the task's failure or verification depends on the device, backend, driver, topology, or instruction set. The skill remains hardware-agnostic unless maintainer evidence shows that its guidance must differ.

The first milestone is infrastructure qualification: prove that the selected Intel GPU is visible inside Harbor's isolated container, compile a SYCL program, execute a kernel, and verify its result. This does not by itself prove that a skill improves agent behavior.

## Recommended rollout

| Stage | Method | Why |
| --- | --- | --- |
| First run | Disposable Linux host over SSH | Fastest path with the fewest GitHub security and administration dependencies. |
| Repeated runs | Ephemeral GitHub runner in a private control repository | One job per clean runner, restricted repository access, durable logs and artifacts. |
| Larger pool | Runner scale set or project-owned lab scheduler | Appropriate only after demand and ownership are established. |

Do not attach a persistent privileged runner to pull-request workflows in the public skills repository. A private control repository should check out this public repository at an explicit commit SHA and dispatch only reviewed manual or scheduled jobs.

A copy-ready private repository scaffold is available under [`evaluation/runner-control-repo-template/`](../evaluation/runner-control-repo-template/README.md). Its workflow accepts only a full commit SHA, pins GitHub-authored actions, invokes the reviewed oracle implementation from that exact checkout, writes a job summary, and uploads the complete Harbor evidence even after failures. The project-independent pattern is described in [Private Machine Runner](private-machine-runner.md).

## Host requirements

- Linux x64 host supported by the GitHub runner, preferably Ubuntu 22.04 or 24.04.
- A supported Intel GPU with the host kernel driver, firmware, and Level Zero runtime installed.
- `/dev/dri/renderD*` present.
- Docker Engine with Compose v2.
- Python 3.12 with virtual-environment support.
- At least 4 CPU threads, 16 GB RAM, and 40 GB free disk for the oneAPI image, Harbor layers, workspaces, and results.
- Outbound HTTPS to GitHub, Docker Hub, the model provider when model trials are enabled, and any task-declared public sources.
- An account allowed to run Docker and read the GPU render node.

An Intel Tiber Developer Cloud Max Series instance or an existing UXL/Intel laboratory host can satisfy these requirements. Record the exact device rather than relying on a generic `gpu` label.

The native-Linux task deliberately qualifies the `/dev/dri` path. The separate `sycl-device-discovery-windows-wsl` task qualifies Windows/WSL through `/dev/dxg`, a read-only `/usr/lib/wsl` mount, and Level Zero. Never route one contract to the other lane.

### Qualified Windows/WSL lane

The UXL control plane has a passing Windows/WSL Intel GPU reference:

- private dispatcher: access-controlled `uxlfoundation/uxl-skills-runner-control`;
- runner labels: `uxl,sycl,gpu,intel-gpu,windows-wsl,personal-lab`;
- evaluator commit: `884bc80bff12c4a61adb5c7e2127338a55e6e1fc`;
- qualification: access-controlled GitHub Actions run `32846295857`, reward `1.0`;
- lifecycle: repository-scoped, manual-dispatch, ephemeral runner.

On that workstation, start a waiting one-job runner with the reusable helper in this repository:

```powershell
.\scripts\runner\start-ephemeral-wsl-runner.ps1 `
  -Repository uxlfoundation/uxl-skills-runner-control
```

## 1. Qualify the Linux host

Run these commands on the remote host:

```bash
uname -a
cat /etc/os-release
lspci -nnk | grep -A3 -Ei 'vga|display'
ls -l /dev/dri
docker version
docker compose version
```

If the current account lacks the necessary groups, an administrator can add it and then require a fresh login:

```bash
sudo usermod -aG docker,render,video "$USER"
```

Capture machine-readable provenance from a pinned checkout:

```bash
python3 scripts/capture_hardware_provenance.py \
  --output harbor-jobs/runner-provenance.json \
  --require-intel-gpu
```

The command succeeds when an Intel GPU is enumerated and a render node is present. It never records environment secrets.

## 2. Verify the pinned container can see the GPU

```bash
export INTEL_RENDER_GID="$(stat -c '%g' "$(find /dev/dri -maxdepth 1 -name 'renderD*' -print -quit)")"

docker run --rm \
  --device /dev/dri:/dev/dri \
  --group-add "$INTEL_RENDER_GID" \
  intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c \
  bash -lc 'ONEAPI_DEVICE_SELECTOR=level_zero:gpu sycl-ls'
```

Stop here if the expected Intel GPU is absent. A host driver or container device-permission problem is infrastructure failure, not an evaluator or skill failure.

## 3. Run the Harbor hardware oracle over SSH

From the repository checkout on the remote host:

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

Reward `1.0` requires all of the following inside the Harbor container:

- `sycl-ls` lists an Intel GPU.
- A `/dev/dri/renderD*` node is visible.
- The pinned compiler builds the smoke program.
- `ONEAPI_DEVICE_SELECTOR=level_zero:gpu` selects the GPU.
- The kernel executes and its output is correct.
- The diagnosis covers driver, runtime, device, and smoke-test evidence.

Copy `harbor-jobs/runner-provenance.json` and the complete oracle job directory back to the workstation for dashboard viewing.

## 4. Add an ephemeral GitHub runner

Create a private control repository or use an existing private UXL operations repository. In that repository:

1. Open **Settings → Actions → Runners → New self-hosted runner**.
2. Select Linux x64.
3. Run the exact download and checksum commands GitHub displays on the GPU host.
4. Use the one-time registration token from that page. Do not save it in a file or repository secret.
5. Register a one-job runner with controlled labels:

```bash
export RUNNER_REPOSITORY_URL='<private-control-repository-url>'

./config.sh \
  --url "$RUNNER_REPOSITORY_URL" \
  --token <one-time-registration-token> \
  --labels uxl,sycl,gpu,intel-gpu \
  --ephemeral

./run.sh
```

Use an organization runner group restricted to the control repository when organization administration is available. The workflow should request all labels, but it must still probe the actual hardware because GitHub does not validate custom label truthfulness.

The control workflow should:

1. Check out `uxlfoundation/skills` at an explicit reviewed commit SHA.
2. Capture host provenance.
3. prove container access to `/dev/dri`.
4. Run the Harbor oracle before any model experiment.
5. Upload complete `harbor-jobs/` artifacts even when the job fails.
6. Destroy or reimage the host after the ephemeral runner deregisters.

The public repository's `.github/workflows/harbor-hardware.yml` is a reference implementation for the execution steps. Its runner labels now include `intel-gpu`; use it directly only after accepting the public-repository runner risk.

For a personal or otherwise multi-purpose host, use the private [runner control repository template](../evaluation/runner-control-repo-template/README.md) instead. It adds the `personal-lab` label and deliberately has no pull-request, push, model, or credential-bearing path.

## 5. Run a model experiment

After the oracle succeeds, use the same host, task revision, image, device selector, model, reasoning effort, and attempt count for every arm. Start with a one-attempt no-skill and candidate-skill screen. Use three attempts only after the task shows useful headroom.

The current `sycl-device-discovery` task primarily qualifies infrastructure and may be a ceiling task. Report it as target-hardware execution evidence, not as proof that the skill improves quality. A skill-benefit claim requires a reproducible maintainer incident whose repair can be evaluated on the device.

## Troubleshooting

| Failure | Meaning | Next action |
| --- | --- | --- |
| `/dev/dri` is absent | Host driver or VM device attachment is incomplete | Fix the host before running Harbor. |
| Host sees GPU; container does not | Device mapping or render-group GID is wrong | Recheck `--device`, `INTEL_RENDER_GID`, and Docker permissions. |
| `sycl-ls` sees only CPU | Level Zero runtime or device selector is wrong | Verify driver/runtime versions and clear unintended filters. |
| Harbor reports unsupported GPU allocation | The task is from before Intel `/dev/dri` passthrough was added | Use the updated task without `[environment].gpus`. |
| Kernel compiles but cannot create a GPU queue | Runtime plugin, permissions, or selector failure | Preserve `sycl-probe.json` and compare host versus container discovery. |
| GitHub job remains queued | No online idle runner has every requested label | Check the runner group and `intel-gpu` label. |
