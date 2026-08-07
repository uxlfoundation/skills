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

## Recorded experiments

- [2026-08-07 paired pilot](results/2026-08-07-paired-pilot.md): initial baseline-versus-skill runs for oneMath and oneTBB.

`check_harbor_job.py` is a CI assertion over Harbor's `result.json`; Harbor remains the evaluation harness and result format owner.

The GPU pilot intentionally requests a GPU and is excluded from hosted CI. Run it only on a trusted SYCL-capable runner.
