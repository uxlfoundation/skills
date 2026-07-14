# Evaluator Reporting

Use evaluator reports to measure whether a UXL skill improves agent output compared with a baseline agent that does not see the skill.

## Current Report Type

The current report compares two saved answer directories:

- `baseline`: answers from the agent without the skill.
- `skill_explicit`: answers from the same agent/model when explicitly told to use the skill.

The report scores each answer with the existing eval checks and computes:

- Baseline average.
- Skill-assisted average.
- Skill delta.
- Per-skill wins, losses, ties, missing answers, and forbidden-claim hits.

## Generate Prompts

```powershell
python scripts/run_evals.py --write-prompts eval-prompts
```

## Collect Answers

For each selected prompt, save raw answers as:

```text
eval-answers-baseline/<skill>/<eval-id>.md
eval-answers-skill-explicit/<skill>/<eval-id>.md
```

Use the same model, tool, repository revision, and prompt text for both arms. Record the model/tool version in the report notes or surrounding issue/PR.

## Produce a Scorecard

```powershell
python scripts/compare_eval_arms.py `
  --baseline-dir eval-answers-baseline `
  --skill-dir eval-answers-skill-explicit `
  --output-dir eval-results/manual-run `
  --label manual-run
```

Filter to a subset while iterating:

```powershell
python scripts/compare_eval_arms.py `
  --baseline-dir eval-answers-baseline `
  --skill-dir eval-answers-skill-explicit `
  --skill uxl-onemath `
  --eval onemath-dispatch-choice `
  --output-dir eval-results/onemath-smoke `
  --label onemath-smoke
```

The script writes:

- `scorecard.json`
- `scorecard.md`

`eval-results/` is ignored by git. Commit only curated summaries or release evidence, not raw exploratory runs.

## Interpreting Results

Use the term-based score as a first-pass signal, not final proof. A promotion report should also include manual or maintainer review for:

- Whether the recommendation is actually correct.
- Whether source-grounding is current and sufficient.
- Whether the skill avoided unsupported compatibility or performance claims.
- Whether validation steps are realistic for the project.

For a promotion candidate, run at least three trials per arm and report the average delta.

## Executable Task Smoke

Executable task fixtures live under `evaluation/tasks/`. Validate task metadata and oracle solutions with:

```powershell
python scripts/validate_executable_tasks.py --run-oracles
```

The first task, `onetbb-histogram-local-aggregation`, is a hosted-CI-safe CPU task that models the oneTBB partition-local aggregation pattern without requiring oneTBB to be installed.

Candidate outputs should be saved as one directory per task:

```text
eval-executable-candidates/<task-id>/<expected-artifact>
```

The runner also accepts `eval-executable-candidates/<skill>/<task-id>/...` and `eval-executable-candidates/<skill>--<task-id>/...`.

Produce an executable task scorecard with:

```powershell
python scripts/run_executable_tasks.py `
  --candidate-dir eval-executable-candidates `
  --output-dir eval-results/executable-manual-run `
  --label executable-manual-run
```

The script writes:

- `executable-scorecard.json`
- `executable-scorecard.md`

Use `--fail-under-pass-rate` for CI gates once a task set is stable.

## Commit Dashboard

CI generates a dashboard bundle after the answer-quality and executable scorecards finish. The smoke dashboard covers every answer-quality eval case with generated fixture arms, plus the hosted-CI executable task fixtures. The bundle contains:

- `dashboard/index.html`: static dashboard for the current run plus any supplied history.
- `dashboard/dashboard-data.json`: normalized data for commit/run trend reporting.
- `dashboard/run-record.json`: the current commit's normalized evaluator record.
- `dashboard/summary.md`: the concise Markdown summary appended to GitHub Actions.

Generate the same bundle locally with:

```powershell
python scripts/generate_eval_dashboard.py `
  --answer-scorecard eval-results/manual-run/scorecard.json `
  --executable-scorecard eval-results/executable-manual-run/executable-scorecard.json `
  --output-dir eval-results/dashboard-manual-run `
  --label manual-run
```

Pass previous `dashboard-data.json` files with `--history-file` to show commit trends and detect drops from the prior run. The first CI version uploads the dashboard as a workflow artifact named `uxl-eval-dashboard`; a later GitHub Pages workflow can publish the same `index.html` and JSON files for long-lived project reporting.

## Real Model Arms

Use `scripts/run_answer_model_arms.py` to replace generated fixtures with answers from real agents or model CLIs. The runner invokes one command for the baseline arm and one command for the skill-explicit arm for each selected eval.

Each command receives the prompt on stdin and through environment variables:

- `UXL_EVAL_ARM`
- `UXL_EVAL_SKILL`
- `UXL_EVAL_ID`
- `UXL_EVAL_PROMPT`
- `UXL_EVAL_PROMPT_FILE`
- `UXL_EVAL_OUTPUT_FILE`
- `UXL_SKILL_PATH`
- `UXL_REPO_ROOT`

If the command writes `UXL_EVAL_OUTPUT_FILE`, that file is used. Otherwise stdout is captured as the answer.
Command templates may also use `{prompt_file}`, `{output_file}`, `{skill}`, `{eval_id}`, `{skill_path}`, `{repo_root}`, `{arm}`, and `{prompt}` placeholders.

Example shape:

```powershell
python scripts/run_answer_model_arms.py `
  --baseline-command "your-agent --no-skills < `"{prompt_file}`"" `
  --skill-command "your-agent --skills-dir skills < `"{prompt_file}`"" `
  --output-dir eval-results/real-model/answers `
  --timeout-seconds 600

python scripts/compare_eval_arms.py `
  --baseline-dir eval-results/real-model/answers/baseline `
  --skill-dir eval-results/real-model/answers/skill-explicit `
  --output-dir eval-results/real-model/answer-scorecard `
  --label real-model
```

By default the baseline arm receives the same task with the `$uxl-*` skill trigger stripped, while the skill-explicit arm receives the original skill-triggering prompt. Use `--same-prompt` only when the baseline environment is guaranteed not to load or interpret UXL skills.
