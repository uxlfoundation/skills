# Hardware and Backend Evaluation

This document describes how to test UXL skill quality on real hardware and backend runtimes. It is intentionally vendor-neutral: UXL is a collaboration across many members, so the evaluator should support CPU, GPU, accelerator, and distributed environments from any participating ecosystem.

## Runner Model

Use GitHub self-hosted runners in a restricted organization runner group. Do not run these jobs on public fork pull requests. Trigger them only by manual dispatch, trusted branch, scheduled run, or maintainer-approved workflow.

Recommended generic labels:

- `self-hosted`
- `linux`
- `x64`
- `uxl`
- `cpu`
- `sycl`
- `gpu` when a GPU is available
- `distributed` when multi-rank or multi-node tests are available

Member or vendor-specific labels may be added by runner owners, but the evaluator should not require them.

Example workflow target:

```yaml
runs-on: [self-hosted, linux, x64, uxl, cpu]
```

GPU jobs should use:

```yaml
runs-on: [self-hosted, linux, x64, uxl, sycl, gpu]
```

## Host Requirements

CPU baseline:

- Linux x86_64.
- CPU supported by the target UXL library and toolchain.
- Git, Python 3.12 or newer, CMake, Ninja.
- Compiler/runtime suitable for the target UXL examples.

GPU or accelerator baseline:

- GPU or accelerator with the required drivers and backend runtime installed.
- `sycl-ls` reports at least one target device for SYCL tasks.
- Backend-specific runtime probes are available when relevant.
- Container access to required accelerator devices if jobs run inside containers.

## Probe Job

Start with a non-mutating probe:

```bash
python skills/uxl-sycl-build-debug/scripts/sycl_probe.py
sycl-ls || true
c++ --version || clang++ --version || true
cmake --version
```

Capture the output as a workflow artifact. The evaluator should classify probe failure separately from agent failure.

## First Executable Tasks

Start small:

1. oneTBB CPU task: fix unsafe shared histogram update and pass a deterministic verifier.
2. oneDPL or oneMath accelerator task: compile a tiny SYCL program, select the requested device/backend, run it, and verify numeric output.

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

Report hardware/backend results separately from hosted CI:

- Hardware tier.
- Device list.
- Compiler/runtime versions.
- Backend/runtime family when known.
- Agent/model/harness.
- Skill arm versus baseline arm.
- Pass/fail outcome.
- Runtime and command-count metrics.

Hardware/backend results should inform skill promotion, but hosted CI should remain the fast default gate for ordinary documentation and skill edits.

## References

- GitHub self-hosted runner labels: https://docs.github.com/actions/hosting-your-own-runners/using-labels-with-self-hosted-runners
- GitHub self-hosted runner security guidance: https://docs.github.com/actions/hosting-your-own-runners/managing-self-hosted-runners/managing-access-to-self-hosted-runners-using-groups
- SYCL specification registry: https://registry.khronos.org/SYCL/
- oneAPI specification: https://oneapi-spec.uxlfoundation.org/specifications/oneapi/latest/
