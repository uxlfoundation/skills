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
