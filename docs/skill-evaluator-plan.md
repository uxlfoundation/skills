# UXL Skill Evaluator Plan

This project should build its own evaluator for UXL skills. External projects can inform the design, but the evaluator should live here because UXL skill quality depends on UXL-specific APIs, build systems, correctness expectations, and Intel hardware behavior.

Nikolay's `agent-benchmark` project is a useful reference, especially its treatment-arm comparison idea and executable task track. It should not be a required dependency unless we decide to reuse a stable module deliberately.

## Objectives

Measure whether a skill improves agent behavior compared with a baseline agent that does not see the skill.

The evaluator should answer:

1. Did the skill trigger when it should, and stay quiet when it should not?
2. Did the agent choose the right UXL API, workflow, backend, and validation plan?
3. Did the agent ground current claims in official sources?
4. Did generated code configure, build, and run?
5. On Intel hardware, did the code select the expected device and produce correct results?
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

Current implementation: `scripts/validate_catalog.py`, `scripts/run_evals.py --validate`, `scripts/check_links.py`, `scripts/generate_agent_wrappers.py --check`, and agnix.

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

### Track 4: Intel Hardware Validation

Runs on restricted self-hosted Intel hardware, not on public fork PRs.

Use this track to test that skill-assisted agents can produce code that actually works on Intel CPU/GPU systems.

Hardware tiers:

- `intel-cpu-oneapi`: Intel Xeon or Core CPU with oneAPI compiler/runtime.
- `intel-gpu-level-zero`: Intel GPU with Level Zero runtime visible to SYCL.
- `intel-multi-gpu`: optional future tier for multi-tile or multi-card tests.
- `intel-distributed`: optional future tier for oneCCL multi-node or multi-rank tests.

Minimum probes:

- `sycl-ls`.
- `icpx --version` or `clang++ --version` for the selected toolchain.
- `cmake --version`.
- `clinfo` or Level Zero device listing when available.
- `python skills/uxl-sycl-build-debug/scripts/sycl_probe.py`.

The first Intel-hardware milestone should be one small SYCL compile/run task plus one library-specific task, probably oneTBB on CPU and oneDPL or oneMath on Intel GPU.

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
- For hardware-sensitive skills, at least one successful Intel-hardware task or a documented reason why hardware execution is not applicable.

## Phased Implementation

### Phase 1: Evaluation Contract

- Commit this plan.
- Add `evaluation/uxl-skill-evaluator.v0.json`.
- Add `scripts/validate_evaluator_plan.py`.
- Keep current eval prompts as seed answer-quality tasks.

### Phase 2: Answer-Quality Runner

- Extend `scripts/run_evals.py` or add a new runner that can compare `baseline` and `skill_explicit` answer directories.
- Emit JSON reports with per-dimension scores and skill deltas.
- Support a structured rubric JSON for optional model or human judges.

### Phase 3: Trace Runner

- Add harness adapters for Codex, Claude Code, and a generic command runner.
- Save trace JSONL, command logs, final answer, and produced artifacts.
- Add deterministic trace checks.

### Phase 4: Executable Task Harness

- Add `evaluation/tasks/` with one or two starter tasks.
- Verify oracle solutions in CI.
- Run agent-produced solutions in disposable workspaces.

### Phase 5: Intel Hardware Track

- Add a manually dispatched GitHub workflow targeting restricted self-hosted Intel runners.
- Start with probe-only jobs, then add one CPU and one GPU task.
- Publish artifacts but keep raw model traces out of git unless curated.

## Useful External Ideas

- OpenAI skill eval pattern: prompt, captured run, checks, score; start with deterministic trace/artifact checks, then add structured rubric judging. See https://developers.openai.com/blog/eval-skills.
- Anthropic agent eval guidance: combine code-based, model-based, and human graders; coding agents need stable environments and outcome tests. See https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents.
- LangChain readiness checklist: separate capability and regression evals, run multiple trials, review failures, and track efficiency metrics. See https://www.langchain.com/blog/agent-evaluation-readiness-checklist.
- SWE-bench and Terminal-Bench: use isolated environments and executable verification. See https://github.com/swe-bench/SWE-bench and https://github.com/harbor-framework/terminal-bench.
- Ragas: useful pattern for separating retrieval/context quality from answer quality when we later test skill-plus-docs or MCP-backed arms. See https://docs.ragas.io/en/stable/.
- `agent-benchmark`: useful ideas include treatment arms, product/intent registries, static docs metrics, and executable tasks. Treat it as an idea source unless we explicitly vendor or depend on stable pieces. See https://github.com/napetrov/agent-benchmark/tree/main.
