# Forward Testing

Use Harbor jobs to learn whether a skill improves real agent behavior. Harbor owns agent execution, isolated environments, repeated trials, trajectories, artifacts, and result viewing. UXL owns the tasks, verifiers, treatments, and promotion thresholds.

## Run With and Without Skills

For each Harbor task, run three jobs with the same task revision, agent, model, attempt count, timeouts, and environment:

- Baseline: do not pass `--skill` or a skill-specific extra instruction.
- Previous skill: pass the skill from the comparison Git revision.
- Candidate skill: pass the candidate skill from the current working tree.

Use at least three attempts per arm for calibration and five for promotion evidence. Harbor stores the task result, reward, verifier logs, trajectory, timing, usage, and collected artifacts under `harbor-jobs/`.

For triage claims, the failure must reproduce in the declared environment and the task must exercise reproduce, investigate, repair, and verify. Fixture and review tasks can support reasoning coverage but are not substitutes for live triage.

## Review Results

Run `harbor view harbor-jobs` and compare the paired jobs. Review deterministic rewards and trajectories for:

- Correct API or workflow choice.
- Use of official sources when current support matters.
- Appropriate clarifying questions.
- Clear correctness validation.
- No unsupported performance or compatibility claims.
- Verified success before efficiency is compared.
- Uncached input, cached input, output tokens, cost, and runtime.
- Cost and token burn per verified success.

For skill promotion, record the mean reward for every arm, verified-success count, efficiency deltas, trial count, agent/model, Harbor version, task revision, skill digest, and execution environment. Keep the raw Harbor job directories or uploaded private job references.

Exclude runner, network, provisioning, and service failures and rerun the unchanged trial. Preserve and report those failures separately rather than scoring them as skill failures.

## Record Evidence

When a skill is ready for review, update the skill card with:

- Date tested.
- Agent/tool used.
- Model, if known.
- Harbor task IDs tested.
- Summary of failures.
- Changes made after testing.

Mark a skill `reviewed` or `project-owned` only after the owning project maintainers have reviewed the content and the promotion criteria in `docs/release-and-promotion-policy.md` are satisfied.
