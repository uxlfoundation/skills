# Windows/WSL Intel GPU runner packet

This directory contains the planning and qualification records for a manually enabled Windows/WSL Intel GPU evaluation runner.

## Documents

- [Runner handoff](windows-wsl-intel-gpu-runner-handoff.md) — qualification result, proposed lane contract, and follow-up work.
- [Preparation report](uxl-runner-prep-report.md) — captured host and runtime evidence.
- [Codex preparation prompt](personal-intel-gpu-runner-codex-prompt.md) — reusable instructions for preparing a comparable host.

Supporting scripts live in [`scripts/runner/`](../../scripts/runner/). Historical execution logs are retained outside the repository under `../artifacts/runner-prep-2026-08-18/` at the UXL workspace level.

The Windows/WSL lane is separate from the native-Linux `/dev/dri` runner contract. Do not register or enable a self-hosted runner until its workflow, labels, repository scope, and reviewed commit are explicit.
