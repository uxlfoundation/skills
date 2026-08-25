# UXL Agent Skills

Public catalog for agent skills that teach AI coding agents how to use UXL Foundation oneAPI libraries correctly.

This repository is the central distribution catalog for UXL skills. Skill status is still explicit: the current catalog release is public, while individual skills remain `incubating` or `pilot` until reviewed by the owning projects. The working recommendation, subject to UXL project review, is a hybrid source-of-truth model:

- Library-owned skills live first in the owning project repositories.
- This catalog mirrors reviewed skills for discovery, installation, validation, and release governance.
- Cross-cutting skills that span multiple projects live directly here.

## Skills

| Skill | Purpose |
| --- | --- |
| `uxl-onednn` | oneDNN primitive selection, memory layout, graph/fusion, backend, and `benchdnn` workflows |
| `uxl-onemath` | oneMath domain selection, runtime/compile-time dispatch, backend setup, and build guidance |
| `uxl-onedal` | oneDAL native C++ and scikit-learn acceleration planning, data tables, and validation |
| `uxl-onetbb` | oneTBB parallel algorithm, flow graph, task arena, and concurrency pattern selection |
| `uxl-onedpl` | oneDPL host/device execution policy usage and SYCL algorithm migration |
| `uxl-oneccl` | oneCCL collectives, launch setup, plugins, distributed training integration, and hang triage |
| `uxl-sycl-build-debug` | Cross-project SYCL compiler, linker, device discovery, and runtime setup diagnosis |
| `uxl-performance-validation` | Cross-project correctness, benchmark, profiling, and speedup evidence workflow |

The catalog manifest is [skills.yaml](skills.yaml). Human-readable review records live in [skill-cards](skill-cards).

## Proposed Placement Model

Use this repo as an incubator first. Once project maintainers review the skill contents, copy each project skill into the matching repository under `skills/<skill-name>/`, then mirror it back here with provenance in release metadata.

Recommended product ownership:

- `uxl-onednn` -> `uxlfoundation/oneDNN`
- `uxl-onemath` -> `uxlfoundation/oneMath`
- `uxl-onedal` -> `uxlfoundation/oneDAL`
- `uxl-onetbb` -> `uxlfoundation/oneTBB`
- `uxl-onedpl` -> `uxlfoundation/oneDPL`
- `uxl-oneccl` -> `uxlfoundation/oneCCL`
- `uxl-sycl-build-debug` and `uxl-performance-validation` -> central `uxlfoundation/skills`

## Development

Validate the catalog locally:

```powershell
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
harbor run --path evaluation/harbor/tasks --agent oracle --include-task-name onetbb-histogram-local-aggregation --include-task-name onemath-runtime-library-missing --job-name uxl-oracle-smoke --jobs-dir harbor-jobs --n-concurrent 2 --yes
python scripts/generate_agent_wrappers.py --check
python scripts/check_links.py --timeout 15 --retries 1
agnix . --config .agnix.toml
```

Validate an individual skill with Codex's skill creator helper:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\uxl-onemath
```

Harbor evaluation tasks, baseline/treatment commands, and hardware guidance live in [evaluation/harbor/README.md](evaluation/harbor/README.md). Harbor `0.20.0` is the pinned evaluation harness.

Start with the one-page [evaluator quickstart](docs/evaluator-quickstart.md), then use the [evaluator operator guide](docs/evaluator-operator-guide.md) for complete instructions. They explain how to modify a skill or task, validate it, run an oracle, compare no-skill/previous/candidate arms, inspect exact prompts and success criteria, and retain experiment results. The [self-hosted runner policy](docs/self-hosted-runners.md) describes the hardware-neutral execution contract. The current [Intel GPU adapter](docs/intel-gpu-runner.md) and access-controlled `uxlfoundation/uxl-skills-runner-control` dispatcher implement that contract. The reusable [private-machine runner pattern](docs/private-machine-runner.md) is suitable for other projects. The owner-only [evaluator control room](https://uxl-evaluator-control-room.melonakos.chatgpt.site) is deployed from [evaluation/dashboard](evaluation/dashboard).

## Agent Tools

This repo includes instruction files for Codex/AGENTS-compatible agents, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Continue, Aider, Windsurf, Cline, Devin-style workflows, and OpenHands-style repository skills. See [agent-tooling.md](docs/agent-tooling.md).

The CI workflow also runs `agent-sh/agnix` against the repository agent configuration files using [.agnix.toml](.agnix.toml).

Install and usage guidance lives in [install-and-use.md](docs/install-and-use.md). The Harbor-based forward-test workflow lives in [forward-testing.md](docs/forward-testing.md).

The [UXL agentic plan](docs/agentic-plan.md) translates the agentic-pipeline steering proposal into a two-quarter, benchmark-led execution program.

The [2026 H2 roadmap](docs/roadmap-2026-h2.md) prioritizes catalog promotion, maintainer review, missing evaluation evidence, and the first agentic proof point. Windows/WSL Intel GPU qualification material is grouped under [docs/runner](docs/runner/README.md).

Regenerate tool wrappers after changing canonical guidance:

```powershell
python scripts/generate_agent_wrappers.py
```

Then review the generated files and run `python scripts/generate_agent_wrappers.py --check`.

## Release and Promotion

The repository is already public and released. Promotion criteria remain because individual skills are still incubating or pilot-quality until maintainers review them.

- Catalog releases make a pin-able snapshot of this repository.
- Skill promotion requires maintainer review, current source verification, forward-test evidence, and updated skill-card evidence before a skill can be marked `reviewed` or `project-owned`.

See [release-and-promotion-policy.md](docs/release-and-promotion-policy.md) and the release ledger in [docs/releases](docs/releases).
