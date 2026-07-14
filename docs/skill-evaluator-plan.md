# UXL Skill Evaluator Plan

This project should build its own evaluator for UXL skills. External projects can inform the design, but the evaluator should live here because UXL skill quality depends on UXL-specific APIs, build systems, correctness expectations, and backend or hardware behavior across member ecosystems.

Nikolay's `agent-benchmark` project is a useful reference, especially its treatment-arm comparison idea and executable task track. It should not be a required dependency unless we decide to reuse a stable module deliberately.

## Objectives

Measure whether a skill improves agent behavior compared with a baseline agent that does not see the skill.

The evaluator should answer:

1. Did the skill trigger when it should, and stay quiet when it should not?
2. Did the agent choose the right UXL API, workflow, backend, and validation plan?
3. Did the agent ground current claims in official sources?
4. Did generated code configure, build, and run?
5. On the target backend or hardware tier, did the code select the expected device/runtime and produce correct results?
6. Did the skill reduce avoidable tool churn, unsupported claims, and missing validation steps?

## Design Principles

- Own the UXL evaluator in this repository.
- Compare controlled treatment arms: `baseline`, `skill_explicit`, `skill_auto`, and later `skill_plus_docs`.
- Use deterministic graders first: tests, build status, output files, source-link checks, trace checks, and forbidden-claim checks.
- Use rubric or human judging only for dimensions that cannot be reliably tested in code.
- Keep capability evals separate from regression evals.
- Run multiple trials for non-deterministic agent flows before claiming a statistically meaningful skill delta.
- Store raw traces and artifacts outside git by default; commit only curated fixtures.
- Track efficiency alongside quality: tool calls, command count, token count, wall time, and retry count.

## Evaluation Tracks

### Track 0: Static Skill Quality

Runs in normal GitHub-hosted CI.

Checks:

- `SKILL.md` frontmatter and concise body.
- Source ledgers and local links.
- Eval definitions.
- Agent wrapper consistency.
- Agnix agent-config lint.
- Source freshness metadata for pilot/reviewed skills.

Current implementation: `scripts/validate_catalog.py`, `scripts/run_evals.py --validate`, `scripts/check_links.py`, `scripts/generate_agent_wrappers.py --check`, `scripts/generate_fixture_answer_arms.py`, `scripts/run_answer_model_arms.py`, `scripts/generate_eval_dashboard.py`, and agnix.

### Track 1: Answer Quality Delta

Runs offline and in scheduled/manual CI once model credentials are available.

For each task:

1. Run a baseline agent without the skill.
2. Run the same model with the skill explicitly provided.
3. Later, run an auto-trigger condition where the agent must decide whether to use the skill.
4. Score both answers with deterministic checks and a small structured rubric.
5. Report `skill_delta = skill_explicit_score - baseline_score`.

Initial dimensions:

- API/workflow correctness.
- Source grounding.
- Build/debug specificity.
- Correctness and performance validation discipline.
- Unsupported-claim avoidance.
- Actionability.

### Track 2: Trace and Tool-Use Quality

Runs when the agent harness can capture structured traces.

Checks:

- Skill was loaded or cited when expected.
- Required commands or files appeared in the trace.
- The agent did not skip validation commands for executable tasks.
- The agent did not thrash, loop, or use an unreasonable number of commands.
- Permission and network use stayed within the task policy.

### Track 3: Executable UXL Tasks

Runs in containerized or clean workspaces.

Each executable task should include:

- `task.json`: metadata, required skill, hardware tier, timeout, and expected artifacts.
- `prompt.md`: what the agent receives.
- `starter/`: minimal broken or incomplete project.
- `oracle/`: reference patch or solution notes.
- `verify.py`: deterministic verifier.
- Optional `bench.py`: benchmark or profiling verifier.

Candidate starter tasks:

- oneTBB: fix shared histogram update with partition-local aggregation.
- oneDPL: repair missing synchronization after a device policy algorithm.
- oneMath: diagnose runtime dispatch library path/backend selection failure.
- oneDNN: remove unnecessary reorder or add correctness validation around layout change.
- oneCCL: identify missing wait/barrier or launch environment issue in a small multi-rank test.
- oneDAL: preserve table orientation/dtype and verify metric parity.

### Track 4: Hardware and Backend Validation

Runs on restricted self-hosted or partner-provided hardware, not on public fork PRs.

Use this track to test that skill-assisted agents can produce code that works across relevant UXL-supported CPU, GPU, accelerator, and distributed environments. The evaluator should be vendor-neutral; member-specific hardware is selected by runner labels and task metadata, not by evaluator semantics.

Hardware/backend tiers:

- `cpu_runner`: CPU environment with the needed compiler/runtime and UXL library dependencies.
- `sycl_gpu_runner`: SYCL-capable GPU environment, with the backend runtime selected by the host and supported by the relevant project.
- `distributed_runner`: multi-rank or multi-node environment for oneCCL and distributed oneDAL tasks.
- `backend_specific_runner`: optional project-defined tier for vendor/member-specific backend validation.

Minimum probes:

- `sycl-ls`.
- Compiler version for the selected toolchain.
- `cmake --version`.
- Device/runtime listing such as `clinfo`, `sycl-ls`, CUDA/HIP tools, MPI launcher probes, or project-specific backend probes when available.
- `python skills/uxl-sycl-build-debug/scripts/sycl_probe.py`.

The first hardware/backend milestone should be one small CPU task and one small accelerator task on whatever trusted runner is available. Good starters are oneTBB on CPU and oneDPL or oneMath on a SYCL-capable GPU.

## Metrics

Primary:

- Pass rate by task and skill.
- Skill delta versus baseline.
- Regression pass rate for tasks that were already solved.

Secondary:

- Source-grounding score.
- Correctness-validation score.
- Unsupported-claim violations.
- Build/run success.
- Hardware-device selection success.
- Token and command efficiency.
- Human-review disagreement rate for model-judged dimensions.

## Promotion Thresholds

Before a skill moves from `incubating` or `pilot` to `reviewed`, require:

- Maintainer review.
- At least three answer-quality tasks.
- At least one negative-control task where the skill should not be used.
- Positive skill delta on the skill's core task set.
- No critical unsupported-claim failures.
- For hardware-sensitive skills, at least one successful hardware/backend task or a documented reason why executable hardware validation is not applicable.

## Phased Implementation

### Phase 1: Evaluation Contract

- Commit this plan.
- Add `evaluation/uxl-skill-evaluator.v0.json`.
- Add `scripts/validate_evaluator_plan.py`.
- Keep current eval prompts as seed answer-quality tasks.

### Phase 2: Answer-Quality Runner

- Use `scripts/compare_eval_arms.py` to compare `baseline` and `skill_explicit` answer directories.
- Emit JSON and Markdown reports with per-skill scores and skill deltas.
- Support a structured rubric JSON for optional model or human judges.

### Phase 3: Trace Runner

- Add harness adapters for Codex, Claude Code, and a generic command runner.
- Save trace JSONL, command logs, final answer, and produced artifacts.
- Add deterministic trace checks.

### Phase 4: Executable Task Harness

- Add `evaluation/tasks/` with one or two starter tasks.
- Verify oracle solutions in CI with `scripts/validate_executable_tasks.py --run-oracles`.
- Score agent-produced solutions in disposable workspaces with `scripts/run_executable_tasks.py --candidate-dir <dir>`.

### Phase 5: Hardware and Backend Track

- Add a manually dispatched GitHub workflow targeting restricted self-hosted or partner-provided runners.
- Start with probe-only jobs, then add one CPU and one GPU task.
- Publish artifacts but keep raw model traces out of git unless curated.

## Useful External Ideas

- OpenAI skill eval pattern: prompt, captured run, checks, score; start with deterministic trace/artifact checks, then add structured rubric judging. See https://developers.openai.com/blog/eval-skills.
- Anthropic agent eval guidance: combine code-based, model-based, and human graders; coding agents need stable environments and outcome tests. See https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents.
- LangChain readiness checklist: separate capability and regression evals, run multiple trials, review failures, and track efficiency metrics. See https://www.langchain.com/blog/agent-evaluation-readiness-checklist.
- SWE-bench and Terminal-Bench: use isolated environments and executable verification. See https://github.com/swe-bench/SWE-bench and https://github.com/harbor-framework/terminal-bench.
- Ragas: useful pattern for separating retrieval/context quality from answer quality when we later test skill-plus-docs or MCP-backed arms. See https://docs.ragas.io/en/stable/.
- `agent-benchmark`: useful ideas include treatment arms, product/intent registries, static docs metrics, and executable tasks. Treat it as an idea source unless we explicitly vendor or depend on stable pieces. See https://github.com/napetrov/agent-benchmark/tree/main.
