# UXL Harbor Evaluations

UXL uses [Harbor](https://github.com/harbor-framework/harbor) as the execution harness for skill evaluations. Harbor owns agent integration, isolated environments, trials, trajectories, artifacts, and result viewing. This repository owns UXL tasks, solutions, verifiers, treatment definitions, and promotion policy.

The repository pins Harbor `0.20.0` and runs it with Python 3.12. Disable Harbor telemetry for local and CI evaluation runs:

```powershell
$env:HARBOR_TELEMETRY = "off"
```

## Pilot tasks

- `onetbb-histogram-local-aggregation`: hosted-CPU executable task.
- `onemath-runtime-library-missing`: hosted answer-quality task.
- `sycl-device-discovery`: manually dispatched SYCL GPU task.

## Local smoke tests

Run the hosted pilots with Harbor's oracle agent:

```powershell
harbor run `
  --path evaluation/harbor/tasks `
  --agent oracle `
  --include-task-name onetbb-histogram-local-aggregation `
  --include-task-name onemath-runtime-library-missing `
  --job-name uxl-oracle-smoke `
  --jobs-dir harbor-jobs `
  --n-concurrent 2 `
  --yes

python scripts/check_harbor_job.py `
  harbor-jobs/uxl-oracle-smoke/result.json `
  --expected-trials 2 `
  --reward-floor 1.0
```

Run a controlled baseline without a UXL skill:

```powershell
harbor run --path evaluation/harbor/tasks `
  --include-task-name onemath-runtime-library-missing `
  --agent codex --model "<model>" --n-attempts 3 `
  --job-name onemath-baseline --jobs-dir harbor-jobs --yes
```

Run the matching skill-explicit treatment:

```powershell
harbor run --path evaluation/harbor/tasks `
  --include-task-name onemath-runtime-library-missing `
  --agent codex --model "<model>" --n-attempts 3 `
  --skill skills/uxl-onemath `
  --extra-instruction-path evaluation/harbor/instructions/use-uxl-onemath.md `
  --job-name onemath-skill-explicit --jobs-dir harbor-jobs --yes
```

Use the same agent, model, attempt count, timeouts, and task revision for paired jobs. Inspect results with `harbor view harbor-jobs`.

## Compare a skill change

Use the comparison wrapper to run three matched arms: no skill, the skill from a previous Git revision, and the candidate skill in the current working tree.

```powershell
.\scripts\compare_harbor_skill.ps1 `
  -TaskName onemath-runtime-library-missing `
  -SkillName uxl-onemath `
  -PreviousRef main `
  -Model gpt-5.6-sol `
  -Attempts 3 `
  -DashboardBaseUrl http://127.0.0.1:8080
```

The wrapper keeps the task, model, reasoning effort, attempt count, concurrency, and treatment instruction fixed. It exports the previous skill from `-PreviousRef` and snapshots the candidate skill from the current working tree before any arm runs, so it does not modify the current checkout and later edits cannot change an in-flight comparison. On Windows it uses a native Harbor command when available and otherwise falls back to the configured Ubuntu WSL distribution.

The generated report is written to `harbor-jobs/<job-prefix>-comparison.md`. It includes:

- Candidate reward deltas against both no-skill and previous-skill arms.
- Trial completion, errors, and per-trial reward distributions.
- Component metrics from Harbor's native `result.json`.
- Uncached input, cached input, output tokens, cost, and runtime.
- Git commit/tree provenance and a warning when all arms hit a task ceiling.

Use `-DryRun` to inspect the commands without starting jobs. Use `-FailOnRegression` when an incomplete, errored, or lower-reward candidate should produce a failing exit code. Pass `-JobPrefix` for stable job names and `-ReportPath` when a report should be recorded outside the ignored `harbor-jobs` directory.

## Inspect prompts and criteria

The job viewer and task-definition viewer answer different questions. Run them on separate ports:

```powershell
harbor view harbor-jobs --jobs --port 8080
harbor view evaluation/harbor/tasks --tasks --port 8081
```

In the task-definition viewer:

- **Instruction** is the base task prompt.
- **Configuration** is the task environment and timeout contract.
- **Files** exposes `tests/test.sh` and any verifier source that defines the exact success criterion.

In the job viewer, drill into a job, task, and individual trial:

- **Trajectory** shows the exact composed prompt, including treatment instructions.
- **Verifier** shows the emitted reward and verifier output.
- **Artifacts** shows the answer or code that was scored.
- **Config** confirms the skill path, model, reasoning effort, and extra instruction.

Treat the trial's **Reward** and verifier files as authoritative. A prominent job-list metric may be one rubric component rather than the combined reward.

## Recorded experiments

- [2026-08-07 paired pilot](results/2026-08-07-paired-pilot.md): initial baseline-versus-skill runs for oneMath and oneTBB.

`check_harbor_job.py` is a CI assertion over Harbor's `result.json`; Harbor remains the evaluation harness and result format owner.

The GPU pilot intentionally requests a GPU and is excluded from hosted CI. Run it only on a trusted SYCL-capable runner.
