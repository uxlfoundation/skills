# Windows/WSL Intel GPU runner packet

This directory contains the planning and qualification records for a manually enabled Windows/WSL Intel GPU evaluation runner.

## Documents

- [Runner handoff](windows-wsl-intel-gpu-runner-handoff.md) — qualification result, proposed lane contract, and follow-up work.
- [Preparation report](uxl-runner-prep-report.md) — captured host and runtime evidence.
- [Codex preparation prompt](personal-intel-gpu-runner-codex-prompt.md) — reusable instructions for preparing a comparable host.

Supporting scripts live in [`scripts/runner/`](../../scripts/runner/). Historical execution logs are retained outside the repository under `../artifacts/runner-prep-2026-08-18/` at the UXL workspace level.

The reusable security and dispatch model is summarized in [Private Machine Runner](../private-machine-runner.md).

The Windows/WSL lane is separate from the native-Linux `/dev/dri` runner contract. It is now implemented in a private, repository-scoped control plane and qualified by a reward-1.0 Harbor oracle. Register the machine only through the reviewed manual workflow and ephemeral launcher described in the runner guide.
