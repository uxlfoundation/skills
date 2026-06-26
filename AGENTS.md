# Repository Instructions

This repository maintains UXL Foundation agent skills. `AGENTS.md` is the canonical source of repo guidance for agentic tools; keep tool-specific files short and point them back here.

## Goal

Build a reviewable, evidence-backed catalog of skills that help coding agents use UXL Foundation libraries correctly:

- oneDNN
- oneMath
- oneDAL
- oneTBB
- oneDPL
- oneCCL
- Cross-project SYCL build/debug and performance validation workflows

## Authoring Rules

- Keep each per-skill instruction file concise and procedural. Move deep detail into that skill's references directory.
- Keep each skill's frontmatter to `name` and `description` unless the publishing tool requires more metadata at install time.
- Include both what the skill does and when it triggers in the `description`.
- Prefer project-owned docs, READMEs, examples, tests, benchmarks, and maintainer guidance over generic internet advice.
- Record current official sources in each skill's source ledger.
- Keep `skills.yaml` and the matching skill card synchronized with every skill.
- Add or update eval prompts before broadening scope.
- Report speedups only with correctness checks, baseline timings, and a clear measurement method.
- For "latest version", "current support", release status, or compatibility claims, check upstream docs or releases first.

## Structure

Use this shape for each skill:

```text
skills/<skill-name>/
  SKILL.md
  agents/openai.yaml
  references/official-sources.md
  evals/evals.json
  scripts/
```

Catalog-level files:

```text
skills.yaml
skill-cards/<skill-name>.md
scripts/validate_catalog.py
scripts/run_evals.py
```

Make scripts deterministic, standard-library-first, and safe to run on developer workstations.

## Validation

Run:

```powershell
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
python scripts/generate_agent_wrappers.py --check
python scripts/check_links.py --timeout 15
```

Smoke-test helper scripts:

```powershell
python skills/uxl-sycl-build-debug/scripts/sycl_probe.py
python skills/uxl-performance-validation/scripts/summarize_runs.py <results.csv>
```

When Codex skill tooling is available, also run:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\<skill-name>
```

## Review Standard

Before marking a skill as `reviewed` or `project-owned`, require:

- Maintainer review from the owning project.
- Source links checked against current docs.
- At least three realistic eval prompts.
- One with-skill forward test and one without-skill baseline, when feasible.
- Clear limitations in the skill card.

## Agent Behavior

- Preserve user edits and avoid unrelated refactors.
- Prefer `rg` for search and read local files before editing.
- Use `apply_patch` or tool-native edit mechanisms for manual changes.
- Keep generated instructions high-signal and short.
- If a task depends on current upstream support, browse or otherwise verify official sources before answering.
