# Intel Hardware Evaluation

This document describes how to test UXL skill quality on Intel hardware.

## Runner Model

Use GitHub self-hosted runners in a restricted organization runner group. Do not run these jobs on public fork pull requests. Trigger them only by manual dispatch, trusted branch, scheduled run, or maintainer-approved workflow.

Recommended labels:

- `self-hosted`
- `linux`
- `x64`
- `intel`
- `oneapi`
- `intel-cpu-oneapi`
- `intel-gpu-level-zero` when a GPU is available

Example workflow target:

```yaml
runs-on: [self-hosted, linux, x64, intel, oneapi]
```

GPU jobs should use:

```yaml
runs-on: [self-hosted, linux, x64, intel, oneapi, intel-gpu-level-zero]
```

## Host Requirements

CPU baseline:

- Linux x86_64.
- Intel CPU.
- Git, Python 3.12 or newer, CMake, Ninja.
- Intel oneAPI compiler/runtime or an LLVM SYCL toolchain suitable for UXL examples.

GPU baseline:

- Intel GPU with drivers installed.
- Level Zero runtime visible to SYCL.
- `sycl-ls` reports at least one GPU device.
- Container access to `/dev/dri` if jobs run inside containers.

## Probe Job

Start with a non-mutating probe:

```bash
python skills/uxl-sycl-build-debug/scripts/sycl_probe.py
sycl-ls || true
icpx --version || clang++ --version
cmake --version
```

Capture the output as a workflow artifact. The evaluator should classify probe failure separately from agent failure.

## First Executable Tasks

Start small:

1. oneTBB CPU task: fix unsafe shared histogram update and pass a deterministic verifier.
2. oneDPL or oneMath GPU task: compile a tiny SYCL program, select an Intel GPU, run it, and verify numeric output.

Each task should run in a fresh workspace and produce:

- `probe.json`
- `answer.md`
- `trace.jsonl` when available
- `build.log`
- `test.log`
- `score.json`

## Security Rules

- Do not expose secrets to untrusted PR code.
- Prefer manual dispatch for hardware runs.
- Reset workspaces between jobs.
- Run with the least privileges possible.
- If containers are used for GPU jobs, explicitly pass only required devices, such as `/dev/dri`.

## Reporting

Report Intel-hardware results separately from hosted CI:

- Hardware tier.
- Device list.
- Compiler/runtime versions.
- Agent/model/harness.
- Skill arm versus baseline arm.
- Pass/fail outcome.
- Runtime and command-count metrics.

Hardware results should inform skill promotion, but hosted CI should remain the fast default gate for ordinary documentation and skill edits.

## References

- GitHub self-hosted runner labels: https://docs.github.com/actions/hosting-your-own-runners/using-labels-with-self-hosted-runners
- GitHub self-hosted runner security guidance: https://docs.github.com/actions/hosting-your-own-runners/managing-self-hosted-runners/managing-access-to-self-hosted-runners-using-groups
- Intel SYCL device discovery: https://www.intel.com/content/www/us/en/developer/articles/technical/device-discovery-with-sycl.html
- Intel oneAPI Level Zero backend device discovery: https://www.intel.com/content/www/us/en/docs/dpcpp-cpp-compiler/developer-guide-reference/2023-1/programming-with-intel-oneapi-level-zero-backend.html
