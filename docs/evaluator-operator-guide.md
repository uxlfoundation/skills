# Evaluator Operator Guide

This is the shortest path for changing a UXL skill, running a controlled experiment, and understanding the result. UXL teams define the skills, tasks, verifiers, and experiment policy. Harbor provides agent execution, isolated trials, trajectories, artifacts, metrics, and result viewing.

## The five things to know

| Item | Location | Purpose |
| --- | --- | --- |
| Skill guidance | `skills/<skill>/SKILL.md` | The candidate instructions being evaluated. |
| Evaluation prompt | `evaluation/harbor/tasks/<task>/instruction.md` | What every experiment arm must solve. |
| Success criterion | `evaluation/harbor/tasks/<task>/tests/` | The executable verifier and reward calculation. |
| Portfolio | `evaluation/harbor/suites.json` | Task ownership, capability coverage, environment, and calibration state. |
| Results | `harbor-jobs/<job>/` | Rewards, trajectories, artifacts, token usage, cost, and runtime. |

## 1. Validate the checkout

From the repository root in PowerShell:

```powershell
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
python scripts/validate_harbor_suites.py
python scripts/render_harbor_suites.py --check
python scripts/sync_harbor_answer_checkers.py --check
python -m unittest discover -s tests -p "test_*.py"
```

These checks do not run model experiments. They catch malformed skills, tasks, coverage metadata, generated-file drift, and verifier regressions.

Harbor `0.20.0`, Python 3.12, Docker, and a working agent login or API credential are required for live trials. On Windows, install the pinned Harbor command once with `uv`:

```powershell
uv tool install "harbor==0.20.0" --force
uv tool update-shell
```

Restart PowerShell, then verify `harbor --version` and `docker version`. The repository helpers can also use Harbor `0.20.0` from an isolated WSL environment. On the qualified Windows/WSL workstation it is installed at `/home/uxlrunner/.local/share/uxl-harbor`; model experiments should still use the runner lane declared by the task.

## 2. Modify a skill

Edit the relevant files together:

1. `skills/<skill>/SKILL.md` for concise procedural guidance.
2. `skills/<skill>/references/` for detailed project-owned evidence.
3. `skills/<skill>/evals/evals.json` when the skill's intended behavior changes.
4. `skills.yaml` and `skill-cards/<skill>.md` when scope, status, limitations, or sources change.

Run the validation commands above before starting model experiments. Do not tune a skill against hidden verifier implementation details. Use the task instruction and the real project failure as the contract.

## 3. Modify or add a task

A Harbor task normally contains:

```text
evaluation/harbor/tasks/<task>/
  task.toml
  instruction.md
  environment/
  solution/
  tests/
```

Use `solution/` only as the oracle repair or reference answer. Keep success criteria under `tests/` so the agent cannot read them. Update the matching entry in `evaluation/harbor/suites.json`, then regenerate the human-readable matrix:

```powershell
python scripts/validate_harbor_suites.py
python scripts/render_harbor_suites.py
```

Before model testing, run the oracle. A task is not ready if its reference solution cannot earn the required reward.

## 4. Run one oracle task

This lightweight example checks the task and verifier without calling a model:

```powershell
$env:HARBOR_TELEMETRY = "off"
harbor run `
  --path evaluation/harbor/tasks `
  --agent oracle `
  --include-task-name onemath-runtime-library-missing `
  --job-name guide-oracle `
  --jobs-dir harbor-jobs `
  --yes

python scripts/check_harbor_job.py `
  harbor-jobs/guide-oracle/result.json `
  --expected-trials 1 `
  --reward-floor 1.0
```

Use the task's declared runner tier. Do not run a target-GPU or distributed task on an incompatible host.

## 5. Compare a skill change

Use the wrapper so the task, model, attempt count, reasoning effort, and treatment instruction remain matched:

```powershell
.\scripts\compare_harbor_skill.ps1 `
  -TaskName onemath-runtime-library-missing `
  -SkillName uxl-onemath `
  -PreviousRef origin/main `
  -Model <model> `
  -Attempts 3 `
  -DashboardBaseUrl http://127.0.0.1:8080
```

The three arms are:

1. No skill.
2. The skill exported from `-PreviousRef`.
3. The candidate skill snapshotted from the current working tree.

Start with `-Attempts 1` for a development screen. Use three attempts per arm for calibration and five for promotion evidence. Add `-FailOnRegression` in automation. Lower token use never compensates for fewer verified successes.

The wrapper writes `harbor-jobs/<prefix>-comparison.md`, including reward, completed trials, errors, tokens, cost, runtime, verified successes, tokens per verified success, and links into the dashboard.

## 6. Open the dashboards

```powershell
.\scripts\start_harbor_dashboards.ps1 -NoWsl -OpenBrowser
```

On the qualified Windows/WSL workstation, use:

```powershell
.\scripts\start_harbor_dashboards.ps1 -WslDistribution Ubuntu-24.04
```

The results service indexes job folders when it starts. After completing a new experiment, refresh the index with:

```powershell
.\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart
```

| View | Default URL | Use it for |
| --- | --- | --- |
| Results | `http://127.0.0.1:8080` | Jobs, trials, rewards, trajectories, artifacts, token usage, cost, and runtime. |
| Tasks | `http://127.0.0.1:8081` | Base prompts, task configuration, environment files, and exact verifier source. |

To understand one result:

1. In the task viewer, open the task and read **Instruction**.
2. Open **Files**, then inspect `tests/test.sh` and its verifier source for the exact success criterion.
3. In the results viewer, open the job, task, and individual trial.
4. Read **Trajectory** for the composed prompt and the agent's actions.
5. Read **Verifier** for reward components and failure details.
6. Read **Artifacts** for the submitted answer or repaired code.
7. Read **Config** to confirm the model, skill, task revision, and treatment.

The trial reward and verifier output are authoritative. A job-list column can represent one reward component rather than the final combined score.

## 7. Interpret the comparison

Ask these questions in order:

1. Did the candidate preserve or improve verified success?
2. Were any trials invalid because of runner, network, provisioning, or service failures?
3. On valid verified successes, did the skill reduce total token burn?
4. Did cost and runtime move in the same direction?
5. Do trajectories show that the skill caused the intended better workflow, rather than exploiting task wording?

Classify full-quality tasks as ceiling or smoke coverage when all arms pass. They can still show token-efficiency changes, but they do not prove a quality advantage.

## 8. Retain and share results

`harbor-jobs/` is intentionally ignored by Git. Preserve important experiments in one of these ways:

- Upload the complete job directories as a private CI artifact.
- Copy the comparison summary into `evaluation/harbor/results/` after review.
- Record the model, task revision, skill revision, Harbor version, attempts, environment, and excluded infrastructure failures.

To view a downloaded remote result, extract its job folders under `harbor-jobs/` and restart the results dashboard. Harbor can then render the remote trajectories and artifacts locally.

### Run on specialized hardware

Follow the [self-hosted runner contract](self-hosted-runners.md) whenever faithful reproduction requires a device, backend, topology, driver, or instruction set that hosted runners do not provide. An approved runner checks out a reviewed immutable evaluator revision, qualifies the environment with an oracle, and returns the complete `harbor-jobs/` evidence. It must not accept untrusted pull-request triggers.

The access-controlled `uxlfoundation/uxl-skills-runner-control` repository implements this pattern with an Intel GPU adapter. Its workflow requires a reviewed 40-character evaluator commit SHA, runs only the `sycl-device-discovery-windows-wsl` oracle, and uploads the full job directory without model credentials.

After the job finishes:

1. Open the private control repository's Actions run and read its qualification summary.
2. Download `uxl-windows-wsl-intel-gpu-oracle-<commit>` as a ZIP.
3. Run `python scripts/import_harbor_artifact.py <downloaded-artifact.zip>`.
4. Restart the dashboard with the launcher appropriate to the operator host. On the qualified workstation, stop the existing WSL viewer once and relaunch with `.\scripts\start_harbor_dashboards.ps1 -WslDistribution Ubuntu-24.04`.
5. Inspect the trial, verifier output, `runner-provenance.json`, `sycl-probe.json`, and diagnosis exactly like a local result.

Treat a passed oracle as runner qualification, not skill-benefit evidence. Add a three-arm model experiment only after the oracle passes and a maintainer-backed target-dependent task provides meaningful headroom.

Qualification reference: access-controlled run `32846295857` passed with evaluator commit `884bc80bff12c4a61adb5c7e2127338a55e6e1fc` and reward `1.0`. This run exercised the thin private dispatcher and the reusable implementation in `skills`. The sanitized public evaluator control room is deployed from [`evaluation/dashboard`](../evaluation/dashboard/) by GitHub Pages; raw trajectories and machine evidence remain access-controlled.

The importer refuses archive path traversal and conflicting same-named jobs. If a job name already exists with a different `result.json`, review both copies before explicitly using `--replace`.

## Common problems

| Symptom | Action |
| --- | --- |
| Docker is unavailable | Start Docker Desktop or the Linux Docker daemon, then verify `docker version`. |
| `harbor` is not found in PowerShell | Use the provided WSL-based scripts or install Harbor 0.20.0 in Python 3.12. |
| Dashboard is empty | Confirm the selected folder contains job directories with `result.json`. |
| Candidate looks cheaper but fails more often | Reject the efficiency claim; quality is the gate. |
| Every arm gets full reward | Keep the task as smoke coverage and seek a harder independently phrased task. |
| A hardware task fails before the agent starts | Treat it as infrastructure failure, preserve the logs, repair the runner, and rerun unchanged. |

For the current concrete adapter, continue with [Intel GPU runner setup](intel-gpu-runner.md). Other platforms should provide their own task contract, qualification oracle, labels, and provenance while returning the same Harbor artifact structure.
