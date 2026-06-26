# Forward Testing

Use forward tests to learn whether a skill improves real agent behavior.

## Generate Prompts

```bash
python scripts/run_evals.py --write-prompts eval-prompts
```

This writes one prompt file per eval case.

## Run With and Without Skills

For each prompt, run at least two passes:

- Baseline: agent does not see the skill.
- Skill-assisted: agent is explicitly told to use the matching skill folder.

Save outputs as:

```text
eval-answers/<skill>/<eval-id>.md
```

or:

```text
eval-answers/<skill>--<eval-id>.md
```

Keep raw outputs. Do not rewrite them to make scoring cleaner.

## Score Answers

```bash
python scripts/run_evals.py --answers-dir eval-answers --fail-under 0.8
```

The current scorer is term-based and intentionally simple. Use it as a smoke test, then review answers manually for:

- Correct API or workflow choice.
- Use of official sources when current support matters.
- Appropriate clarifying questions.
- Clear correctness validation.
- No unsupported performance or compatibility claims.

## Record Evidence

When a skill is ready for review, update the skill card with:

- Date tested.
- Agent/tool used.
- Model, if known.
- Prompt IDs tested.
- Summary of failures.
- Changes made after testing.

Mark a skill `reviewed` or `project-owned` only after the owning project maintainers have reviewed the content and the promotion criteria in `docs/release-and-promotion-policy.md` are satisfied.
