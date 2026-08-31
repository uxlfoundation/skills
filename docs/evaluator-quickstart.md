# Evaluator Quickstart

Use this page for the routine loop. The [operator guide](evaluator-operator-guide.md) contains the full explanation and troubleshooting details.

## What you edit

| Goal | File or directory |
| --- | --- |
| Change agent guidance | `skills/<skill>/SKILL.md` and `skills/<skill>/references/` |
| Change a task prompt | `evaluation/harbor/tasks/<task>/instruction.md` |
| Change success criteria | `evaluation/harbor/tasks/<task>/tests/` |
| Change the reference solution | `evaluation/harbor/tasks/<task>/solution/` |
| Change portfolio coverage | `evaluation/harbor/suites.json` |
| Find experiment outputs | `harbor-jobs/<job>/` |

## Validate before spending model tokens

From the repository root in PowerShell:

```powershell
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
python scripts/validate_harbor_suites.py
python scripts/render_harbor_suites.py --check
python scripts/sync_harbor_answer_checkers.py --check
python -m unittest discover -s tests -p "test_*.py"
```

Then run the task's oracle. Replace the example task name:

```powershell
$env:HARBOR_TELEMETRY = "off"
harbor run `
  --path evaluation/harbor/tasks `
  --agent oracle `
  --include-task-name onemath-runtime-library-missing `
  --job-name quickstart-oracle `
  --jobs-dir harbor-jobs `
  --yes

python scripts/check_harbor_job.py `
  harbor-jobs/quickstart-oracle/result.json `
  --expected-trials 1 `
  --reward-floor 1.0
```

Do not spend model tokens until the oracle earns reward `1.0` on the task's declared runner tier.

## Compare a skill change

```powershell
.\scripts\compare_harbor_skill.ps1 `
  -TaskName onemath-runtime-library-missing `
  -SkillName uxl-onemath `
  -PreviousRef origin/main `
  -Model <model> `
  -Attempts 1 `
  -DashboardBaseUrl http://127.0.0.1:8080
```

This produces matched no-skill, previous-skill, and candidate-skill jobs plus `harbor-jobs/<prefix>-comparison.md`. Use one attempt for development, three for calibration, and five for promotion evidence.

## View prompts, criteria, and results

```powershell
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart -OpenBrowser
```

| Dashboard | URL | Read this |
| --- | --- | --- |
| Results | <http://127.0.0.1:8080> | Trial reward, trajectory, composed prompt, verifier output, artifacts, tokens, cost, and runtime |
| Tasks | <http://127.0.0.1:8081> | Base instruction, environment, `tests/test.sh`, and exact verifier source |

In the task dashboard, read **Instruction** and then the files under `tests/`. In the results dashboard, open a job, task, and trial; the trial reward and verifier output are authoritative.

## Decide whether the skill helped

Apply these gates in order:

1. Candidate verified success must match or exceed the baseline.
2. Exclude and separately report infrastructure or service failures.
3. Compare tokens per verified success, not raw tokens from failed answers.
4. Review trajectories to confirm the skill caused the intended workflow.
5. Treat all-arms-pass tasks as smoke or efficiency coverage, not quality evidence.

## Import a remote specialized-hardware result

Use an approved self-hosted runner that follows the [shared runner contract](self-hosted-runners.md). The current [private runner control template](../evaluation/runner-control-repo-template/README.md) demonstrates that contract with one platform adapter. After downloading its artifact ZIP, import and view it with:

```powershell
python scripts/import_harbor_artifact.py <downloaded-artifact.zip>
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart -OpenBrowser
```

The importer rejects path traversal and conflicting same-named jobs, attaches shared runner provenance to the imported job, and records an import manifest. If a passing artifact proposes a public qualification, the importer verifies its schema and evidence hashes and stages it under `harbor-jobs/qualification-review/`; publication remains a manual review step. A reward-1.0 hardware oracle qualifies the runner; it does not by itself prove that a skill is beneficial.

## Preserve evidence

`harbor-jobs/` is ignored by Git. Retain important runs as private CI artifacts and record the task commit, skill revisions, model, reasoning effort, attempt count, Harbor version, runner provenance, and excluded failures. Promote reviewed comparison summaries into `evaluation/harbor/results/` only after the evidence is accepted.
