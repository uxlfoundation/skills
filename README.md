# UXL Agent Skills

Starter catalog for agent skills that teach AI coding agents how to use UXL Foundation oneAPI libraries correctly.

This repository is intended to become the central distribution catalog for UXL skills. The long-term source-of-truth model should be hybrid:

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

## Placement Model

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
python scripts/generate_agent_wrappers.py --check
python scripts/check_links.py --timeout 15
```

Validate an individual skill with Codex's skill creator helper:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\uxl-onemath
```

Emit eval prompts for forward testing:

```powershell
python scripts/run_evals.py --write-prompts eval-prompts
```

Score saved answers:

```powershell
python scripts/run_evals.py --answers-dir eval-answers
```

Accepted answer paths are `eval-answers/<skill>/<eval-id>.md` or `eval-answers/<skill>--<eval-id>.md`.

## Agent Tools

This repo includes instruction files for Codex/AGENTS-compatible agents, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Continue, Aider, Windsurf, Cline, Devin-style workflows, and OpenHands-style repository skills. See [agent-tooling.md](docs/agent-tooling.md).

Install and usage guidance lives in [install-and-use.md](docs/install-and-use.md). Forward-test workflow lives in [forward-testing.md](docs/forward-testing.md).

Regenerate tool wrappers after changing canonical guidance:

```powershell
python scripts/generate_agent_wrappers.py
```

Then review the generated files and run `python scripts/generate_agent_wrappers.py --check`.

## Release Gates

Before publishing any skill:

1. Remove placeholders and stale links.
2. Confirm the owning project maintainer reviewed the skill.
3. Run `scripts/validate_catalog.py`.
4. Run `scripts/run_evals.py --validate`.
5. Run `scripts/check_links.py --timeout 15`.
6. Run realistic with-skill and without-skill evals from each skill's `evals/evals.json`.
7. Add or update a skill card that records owner, sources, limitations, risks, and validation evidence.
8. Publish a tagged release and encourage pinning by tag or commit SHA.
