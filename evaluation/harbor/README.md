# UXL Harbor Evaluations

UXL uses [Harbor](https://github.com/harbor-framework/harbor) as the execution harness for skill evaluations. Harbor owns agent integration, isolated environments, trials, trajectories, artifacts, and result viewing. This repository owns UXL tasks, solutions, verifiers, treatment definitions, and promotion policy.

The repository pins Harbor `0.20.0` and runs it with Python 3.12. Disable Harbor telemetry for local and CI evaluation runs:

```powershell
$env:HARBOR_TELEMETRY = "off"
```

## Skill suites and coverage

[`suites.json`](suites.json) is the machine-readable evaluator portfolio, governed by [`schemas/harbor-suites.schema.json`](../../schemas/harbor-suites.schema.json). It maps every catalog skill to capability classes, implemented tasks, planned tasks, task roles, execution environments, calibration status, reproduction mode, scenario origin, workflow stages, hardware requirements, attempt counts, and promotion guardrails. The generated [capability matrix](CAPABILITY_MATRIX.md) is the human-readable audit.

The [evaluator policy](EVALUATOR_POLICY.md) defines what counts as real end-to-end triage, when target hardware is required, how fixture and review tasks are reported, and why cost per verified success is the primary efficiency metric.

Use the [maintainer failure intake](MAINTAINER_FAILURE_INTAKE.md) before converting a project incident into a task. The evidence baseline is recorded in the [2026-08-10 reproducibility audit](results/2026-08-10-reproducibility-audit.md). Candidate decisions are recorded in [maintainer incident sourcing wave 1](results/2026-08-10-incident-sourcing-wave-1.md), [wave 2](results/2026-08-11-incident-sourcing-wave-2.md), and [wave 3](results/2026-08-11-incident-sourcing-wave-3.md).

The v1 portfolio targets 49 tasks across all eight skills. Every skill must cover correctness, selection, integration, debugging, and performance, with at least five tasks and at least two intended to be discriminating. A task that reaches a model ceiling remains useful as smoke or regression coverage but does not satisfy the discriminating-task target.

Answer-quality fixtures test interpretation and reasoning but do not receive live-triage credit. A debugging capability must have planned coverage from a task that reproduces live and exercises reproduce, investigate, repair, and verify. Implemented real end-to-end credit additionally requires a maintainer incident or upstream regression as the task origin.

Validate and regenerate the portfolio with:

```powershell
python scripts/validate_harbor_suites.py
python scripts/render_harbor_suites.py
```

CI uses `python scripts/render_harbor_suites.py --check` to prevent the generated matrix from drifting from the manifest.

New grouped answer-quality tasks can use [`shared/structured_answer.py`](shared/structured_answer.py) with a task-local `tests/rubric.json`. Run `python scripts/sync_harbor_answer_checkers.py` after adding or changing these tasks; CI checks that every vendored verifier matches the shared source.

## Hosted tasks

- `oneccl-datatype-count-mismatch`: hosted structured collective-contract task.
- `oneccl-async-allreduce-wait`: hosted-CPU executable async-completion and buffer-lifetime task.
- `oneccl-divergent-collective-sequence`: hosted structured collective-hang task.
- `onedal-batch-online-distributed-choice`: hosted structured computation-mode decision task.
- `onedal-sklearn-or-native-kmeans`: hosted structured interface-selection task.
- `onedal-table-orientation-regression`: hosted-CPU executable oneDAL table-contract and metric-parity task.
- `onedal-extra-trees-random-split`: hosted-CPU source-level task sourced from oneDAL issue #3648, with public and hidden weighted quality-regression cases.
- `onednn-framework-blocked-layout`: hosted structured layout-integration task.
- `onednn-convolution-fusion-parity`: hosted-CPU executable post-op order and residual-destination task.
- `onednn-extra-reorder-regression`: hosted-CPU executable constant-weight layout-cache task using oneDNN verbose evidence.
- `onednn-benchdnn-no-ref-memory`: hosted-CPU executable task sourced from a public `benchdnn` mode regression.
- `onedpl-missing-device-synchronization`: hosted structured async-device task.
- `onedpl-move-only-numeric-accumulator`: hosted-CPU source-repair task sourced from oneDPL issue #1955, covering move-only accumulators across parallel numeric backends.
- `onedpl-stable-ordering-contract`: hosted-CPU executable oneDPL stable-order contract task.
- `onetbb-bounded-image-flow-graph`: hosted structured backpressure and scheduler task.
- `onetbb-cancellation-exception-propagation`: hosted-CPU executable bounded-ownership and per-job-failure smoke task.
- `onetbb-histogram-local-aggregation`: hosted-CPU executable smoke task.
- `onetbb-join-node-ordering`: hosted-CPU executable task sourced from a public maintainer incident about flow-graph ordering.
- `onetbb-grainsize-affinity-regression`: hosted evidence-driven grainsize, cache-affinity, and NUMA-placement diagnostic task.
- `onetbb-nested-thread-pool-arena`: hosted-CPU executable process-wide runtime-budget task.
- `onetbb-stable-compaction-scan`: harder hosted-CPU task for deterministic prefix-scan reasoning.
- `onemath-runtime-library-missing`: hosted structured diagnostic-answer task.
- `onemath-deprecated-header-include`: hosted-CPU preprocessing task sourced from a public compatibility-header incident.
- `performance-benchmark-report-repair`: hosted-CPU executable reporting task.
- `performance-cgroup-concurrency-quota`: hosted-CPU oneTBB resource-constraint task sourced from a public cgroup quota incident.
- `performance-floating-reduction-tolerance`: hosted-CPU executable numerical-validation task.
- `performance-tiny-async-gpu-claim`: hosted structured benchmark-review task.
- `sycl-cmake-compiler-cache`: hosted structured toolchain-diagnosis task.
- `sycl-loader-plugin-mismatch`: hosted structured runtime-loader task.
- `sycl-selector-silent-cpu-fallback`: hosted-CPU executable runtime-device-proof task.
- `sycl-device-discovery`: manually dispatched SYCL GPU task.

## Local smoke tests

Run the hosted pilots with Harbor's oracle agent:

```powershell
harbor run `
  --path evaluation/harbor/tasks `
  --agent oracle `
  --include-task-name oneccl-async-allreduce-wait `
  --include-task-name oneccl-datatype-count-mismatch `
  --include-task-name oneccl-divergent-collective-sequence `
  --include-task-name onedal-batch-online-distributed-choice `
  --include-task-name onedal-sklearn-or-native-kmeans `
  --include-task-name onedal-table-orientation-regression `
  --include-task-name onedal-extra-trees-random-split `
  --include-task-name onednn-framework-blocked-layout `
  --include-task-name onednn-convolution-fusion-parity `
  --include-task-name onednn-extra-reorder-regression `
  --include-task-name onednn-benchdnn-no-ref-memory `
  --include-task-name onedpl-missing-device-synchronization `
  --include-task-name onedpl-move-only-numeric-accumulator `
  --include-task-name onedpl-stable-ordering-contract `
  --include-task-name onemath-deprecated-header-include `
  --include-task-name onemath-runtime-library-missing `
  --include-task-name onetbb-bounded-image-flow-graph `
  --include-task-name onetbb-cancellation-exception-propagation `
  --include-task-name onetbb-grainsize-affinity-regression `
  --include-task-name onetbb-histogram-local-aggregation `
  --include-task-name onetbb-join-node-ordering `
  --include-task-name onetbb-nested-thread-pool-arena `
  --include-task-name onetbb-stable-compaction-scan `
  --include-task-name performance-benchmark-report-repair `
  --include-task-name performance-cgroup-concurrency-quota `
  --include-task-name performance-floating-reduction-tolerance `
  --include-task-name performance-tiny-async-gpu-claim `
  --include-task-name sycl-cmake-compiler-cache `
  --include-task-name sycl-loader-plugin-mismatch `
  --include-task-name sycl-selector-silent-cpu-fallback `
  --job-name uxl-oracle-smoke `
  --jobs-dir harbor-jobs `
  --n-concurrent 4 `
  --yes

python scripts/check_harbor_job.py `
  harbor-jobs/uxl-oracle-smoke/result.json `
  --expected-trials 30 `
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
- Verified successes, token burn per verified success, and cost per verified success.
- Git commit/tree provenance and a warning when all arms hit a task ceiling.

Use `-DryRun` to inspect the commands without starting jobs. Use `-FailOnRegression` when an incomplete, errored, or lower-reward candidate should produce a failing exit code. Pass `-JobPrefix` for stable job names and `-ReportPath` when a report should be recorded outside the ignored `harbor-jobs` directory.

On Windows/WSL runners, add `-GuardWslCrashDumps` for tasks that intentionally crash a Linux process while reproducing a historical failure. The opt-in guard truncates only new `%TEMP%\wsl-crashes\wsl-crash-*.dmp` files while the comparison is active; task output, exit status, Harbor artifacts, and verifier behavior remain unchanged. This prevents repeated expected crashes from exhausting the Windows host disk. Prefer updating WSL and setting `maxCrashDumpCount=0` when the runner permits an administrator-approved WSL update.

Use `-VerifiedRewardFloor` when a task's deterministic success threshold differs from the portfolio default. Quality remains the gate: lower cost cannot compensate for fewer verified successes.

Total token burn per verified success is the primary efficiency measure. Cost per verified success and runtime remain useful secondary measures because pricing and hardware can change independently of the skill.

## Inspect prompts and criteria

The job viewer and task-definition viewer answer different questions. Run them on separate ports:

```powershell
.\scripts\start_harbor_dashboards.ps1 -OpenBrowser
```

The launcher uses native Harbor when `-NoWsl` is supplied and otherwise uses the configured Ubuntu WSL distribution. It is safe to run again when either dashboard is already active. The equivalent direct commands are:

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
- [2026-08-07 evaluator expansion](results/2026-08-07-evaluator-expansion.md): structured oneMath rubric calibration and harder oneTBB executable-task probe.
- [2026-08-08 coverage wave 1](results/2026-08-08-coverage-wave-1.md): six-task expansion, rubric audit, and three-attempt headroom calibration.
- [2026-08-08 coverage wave 2](results/2026-08-08-coverage-wave-2.md): four-task expansion targeting performance, oneTBB, oneCCL, and SYCL gaps.
- [2026-08-08 coverage wave 3](results/2026-08-08-coverage-wave-3.md): executable async-completion, device-proof, and numerical-validation tasks.
- [2026-08-09 oneTBB bounded-flow skill iteration](results/2026-08-09-onetbb-bounded-flow-skill.md): three-arm skill comparison and audited verifier correction.
- [2026-08-10 oneTBB failure-flow generalization probe](results/2026-08-10-onetbb-failure-flow-generalization.md): executable task calibration and implementation-neutral verifier audit.
- [2026-08-10 oneTBB runtime-composition calibration](results/2026-08-10-onetbb-runtime-composition.md): shared-arena executable task, alternate-submission verifier audit, and ceiling classification.
- [2026-08-10 oneTBB grainsize/affinity skill iteration](results/2026-08-10-onetbb-grainsize-affinity-skill.md): evidence-driven task, implementation-neutral rubric audit, and three-attempt skill calibration.
- [2026-08-10 evaluator reproducibility audit](results/2026-08-10-reproducibility-audit.md): schema v2 task audit, live-versus-fixture coverage, hardware requirements, and the next incident-sourcing wave.
- [2026-08-11 maintainer incident sourcing wave 2](results/2026-08-11-incident-sourcing-wave-2.md): verified oneMath installed-header coverage and evidence-based oneDPL toolchain deferral.
- [2026-08-11 maintainer incident sourcing wave 3](results/2026-08-11-incident-sourcing-wave-3.md): verified deterministic oneTBB cgroup-quota triage on a generic hosted CPU.
- [2026-08-11 oneMath compatibility-header calibration](results/2026-08-11-onemath-header-skill-calibration.md): ceiling classification with verified-success token and cost measurements.
- [2026-08-11 performance cgroup-concurrency calibration](results/2026-08-11-performance-cgroup-skill-calibration.md): ceiling classification after the candidate increased token burn at unchanged quality.
- [2026-08-12 oneDNN benchdnn incident](results/2026-08-12-onednn-benchdnn-incident.md): portable AVX2 reproduction of a maintainer-reported no-reference-memory crash, hardened with a hidden fused-convolution shape.
- [2026-08-12 oneDAL mode selection](results/2026-08-12-onedal-mode-selection.md): hardware-agnostic batch/online/distributed decision coverage with deterministic shortcut rejection.
- [2026-08-12 oneDAL table orientation](results/2026-08-12-onedal-table-orientation.md): real oneDAL CPU execution with a square-fixture trap and held-out rectangular parity cases.
- [2026-08-12 oneDAL table calibration](results/2026-08-12-onedal-table-calibration.md): one-attempt three-arm ceiling; candidate token burn increased 17.8% at unchanged quality.
- [2026-08-12 oneDPL stable ordering](results/2026-08-12-onedpl-stable-ordering.md): real oneDPL host-policy execution with equal-key stability and permutation checks.
- [2026-08-12 oneDPL stable-ordering calibration](results/2026-08-12-onedpl-stable-calibration.md): one-attempt three-arm ceiling; the candidate used 9.9% more tokens than the previous skill at unchanged quality.
- [2026-08-12 oneDNN convolution fusion parity](results/2026-08-12-onednn-convolution-fusion-parity.md): real oneDNN CPU execution with fused post-op order, residual initialization, and hidden shape checks.
- [2026-08-12 oneDNN convolution-fusion calibration](results/2026-08-12-onednn-convolution-fusion-calibration.md): one-attempt three-arm ceiling; current skill used 21.5% fewer tokens than the original skill but 6.5% more than no skill.
- [2026-08-13 oneDNN benchdnn incident calibration](results/2026-08-13-onednn-benchdnn-calibration.md): three-attempt quality ceiling with 11.6% fewer tokens per verified success than no skill and 68.1% fewer than the original skill.
- [2026-08-13 oneDAL mode-selection calibration](results/2026-08-13-onedal-mode-calibration.md): audited one-attempt quality ceiling; current skill used 44.2% fewer tokens than the original skill but 4.6% more than no skill.
- [2026-08-13 calibration-state audit](results/2026-08-13-calibration-state-audit.md): introduces `no-lift`, hardens the oneCCL datatype rubric, and corrects four previously ambiguous task states.
- [2026-08-13 oneDAL ExtraTrees incident](results/2026-08-13-onedal-extra-trees-incident.md): live source reproduction, upstream repair, and Harbor baseline/oracle discrimination for oneDAL issue #3648.
- [2026-08-13 oneDAL ExtraTrees calibration](results/2026-08-13-onedal-extra-trees-calibration.md): one-attempt three-arm quality ceiling; the current skill used 7.0% fewer tokens than no skill and 9.9% fewer than the original skill.
- [2026-08-13 oneTBB join-node calibration](results/2026-08-13-onetbb-join-calibration.md): one-attempt three-arm ceiling; every repair passed, while the current skill used 61.0% more tokens than no skill.
- [2026-08-13 oneDNN constant-weight reorder regression](results/2026-08-13-onednn-reorder-regression.md): live oneDNN CPU task that reduces four repeated constant-weight reorders to one while preserving numerical results.
- [2026-08-13 oneDNN reorder calibration](results/2026-08-13-onednn-reorder-calibration.md): one-attempt three-arm ceiling; the current skill used 21.5% more tokens than no skill at unchanged quality.
- [2026-08-13 oneDPL move-only numeric incident](results/2026-08-13-onedpl-move-only-incident.md): live pre-fix reproduction, accepted upstream repair, and Harbor baseline/oracle discrimination for oneDPL issue #1955.
- [2026-08-13 oneDPL move-only numeric calibration](results/2026-08-13-onedpl-move-only-calibration.md): one-attempt three-arm quality ceiling; the current skill used 197.0% more tokens than no skill at unchanged quality.

`check_harbor_job.py` is a CI assertion over Harbor's `result.json`; Harbor remains the evaluation harness and result format owner.

The GPU pilot intentionally requests a GPU and is excluded from hosted CI. Run it only on a trusted SYCL-capable runner.
