# oneTBB runtime-composition calibration: 2026-08-10

This wave implements the planned `onetbb-nested-thread-pool-arena` task. The executable fixture requires an external caller pool to run oneTBB reductions under one process-wide concurrency budget while preserving ordered exact results, input data, all callers, measured resource observations, invalid-input handling, and useful parallelism.

## Fixture calibration

| Fixture | Reward | Meaning |
| --- | ---: | --- |
| Oracle | 1.0000 | One shared arena satisfies every compiled behavioral case. |
| Misleading starter | 0.0000 | A separate arena per caller exceeds the aggregate compute budget. |

The corrected oracle job was `onetbb-runtime-arena-oracle-fix-20260810-112328`. The starter was evaluated directly with the same compiled verifier in the task container.

## Verifier audit

The first no-skill probe returned raw reward 0 because the verifier required the exact source form `.execute(...)`. Artifact review showed a valid alternative: callers submitted reductions to the shared arena with `.enqueue(...)` and waited outside it. Running that saved artifact against an implementation-neutral verifier produced reward 1.0, while the misleading per-caller-arena starter remained rejected.

The verifier now accepts either `task_arena::execute` or `task_arena::enqueue` while retaining the compiled behavioral checks for exact results, observed process-wide peak, requested caller participation, effective arena concurrency, invalid inputs, and useful parallelism. The discarded development prefix is `onetbb-runtime-arena-probe-20260810-112804`; its incomplete skilled control is not calibration evidence.

## Clean three-arm probe

One matched attempt was then run for no skill, the skill from local `main`, and the candidate working tree. The previous and candidate `SKILL.md` guidance was equivalent for this task, so those arms are controls rather than evidence of a new skill revision.

| Arm | Reward | Errors | Cost (USD) | Runtime | Dashboard |
| --- | ---: | ---: | ---: | ---: | --- |
| No skill | 1.0000 | 0 | $0.352771 | 3m 44s | [Open job](http://127.0.0.1:8080/jobs/onetbb-runtime-arena-probe-fixed-20260810-113437-noskill) |
| Previous skill | 1.0000 | 0 | $0.671903 | 6m 44s | [Open job](http://127.0.0.1:8080/jobs/onetbb-runtime-arena-probe-fixed-20260810-113437-previous) |
| Candidate skill | 1.0000 | 0 | $0.448738 | 4m 19s | [Open job](http://127.0.0.1:8080/jobs/onetbb-runtime-arena-probe-fixed-20260810-113437-candidate) |

The clean no-skill artifact was audited and genuinely used one shared arena, real oneTBB parallel reductions, the complete external caller pool, ordered result storage, and measured concurrency observations. It did not bypass the verifier.

## Portfolio decision

Retain the task as executable smoke coverage and classify it `ceiling`. It raises the portfolio to 19 of 49 implemented tasks and oneTBB to 5 of 7, but it does not add a second discriminating oneTBB task. No three-attempt calibration is warranted because the clean no-skill attempt already reached full reward.

The remaining planned `onetbb-grainsize-affinity-regression` task is the next oneTBB candidate for discriminating coverage. It should present performance evidence that requires experimental diagnosis and measurement design rather than stating the repair architecture in the prompt.

## Validation and provenance

- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per arm: 1; concurrency: 1.
- Task revision: `c7a4369`.
- Previous skill: `main@ce5f7b0`.
- Clean comparison prefix: `onetbb-runtime-arena-probe-fixed-20260810-113437`.
- All three clean jobs completed with zero Harbor exceptions.
- Suite validation and all 25 repository unit tests passed after the verifier correction.

The shared-arena design follows oneTBB's documented `task_arena` concurrency model; `global_control` is a broader scheduler control but does not replace the task's explicit shared execution scope. See the [oneTBB `task_arena` reference](https://uxlfoundation.github.io/oneTBB/main/specification/source/task_scheduler/task_arena/task_arena_cls.html) and [`global_control` reference](https://uxlfoundation.github.io/oneTBB/main/specification/source/task_scheduler/scheduling_controls/global_control_cls.html).
