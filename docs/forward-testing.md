# Forward Testing

Use Harbor jobs to learn whether a skill improves real agent behavior. Harbor owns agent execution, isolated environments, repeated trials, trajectories, artifacts, and result viewing. UXL owns the tasks, verifiers, treatments, and promotion thresholds.

## Run With and Without Skills

For each Harbor task, run at least two jobs with the same task revision, agent, model, attempt count, timeouts, and environment:

- Baseline: do not pass `--skill` or a skill-specific extra instruction.
- Skill-explicit: pass the matching skill with `--skill` and the matching file from `evaluation/harbor/instructions/` with `--extra-instruction-path`.

Use at least three attempts per arm for promotion evidence. Harbor stores the task result, reward, verifier logs, trajectory, timing, usage, and collected artifacts under `harbor-jobs/`.

## Review Results

Run `harbor view harbor-jobs` and compare the paired jobs. Review deterministic rewards and trajectories for:

- Correct API or workflow choice.
- Use of official sources when current support matters.
- Appropriate clarifying questions.
- Clear correctness validation.
- No unsupported performance or compatibility claims.

For skill promotion, record the mean baseline reward, mean skill-explicit reward, delta, trial count, agent/model, Harbor version, task revision, and skill digest. Keep the raw Harbor job directories or uploaded private job references.

## Record Evidence

When a skill is ready for review, update the skill card with:

- Date tested.
- Agent/tool used.
- Model, if known.
- Harbor task IDs tested.
- Summary of failures.
- Changes made after testing.

Mark a skill `reviewed` or `project-owned` only after the owning project maintainers have reviewed the content and the promotion criteria in `docs/release-and-promotion-policy.md` are satisfied.
