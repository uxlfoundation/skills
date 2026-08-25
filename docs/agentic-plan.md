# UXL Agentic Plan

## Objective

Make UXL the evidence-backed systems layer for agentic AI pipelines by delivering a small number of Python-consumable primitives that measurably improve end-to-end agent workloads across CPU, GPU, and distributed systems.

This plan turns the steering-committee thesis in [oneAPI for the Agentic Pipeline](https://docs.google.com/presentation/d/1nM5gQCxkTF4Mu1ueP850CImSo5a6kmUE/edit?slide=id.p1&pli=1#slide=id.p1) into a two-quarter execution program. The deck identifies five recurring stages: prompt assembly, inference, structured parsing, tool execution, and state/KV management. It also identifies four adoption blockers: Python accessibility, integration cost, missing agent-shaped primitives, and the absence of an end-to-end proof point.

## Strategic choice

UXL should begin with an **agentic pipeline benchmark and integration layer**, not a new general-purpose agent framework.

- Existing frameworks continue to own planning, orchestration, tools, and application state.
- UXL libraries own optimized kernels, scheduling, retrieval, communication, and hardware portability.
- Thin Python integrations expose those capabilities where agent developers already work.
- A shared benchmark determines which proposed primitives deserve specification or library investment.

The first reference workload should be a tool-using retrieval agent with parallel tool fan-out. It exercises oneTBB scheduling, oneDAL retrieval/routing, oneDNN/oneMath inference shapes, SYCL device boundaries, and the cross-project performance methodology without requiring every library to change before useful evidence exists.

## Success after two quarters

The program succeeds when it can show all of the following:

1. A reproducible agentic reference workload runs in baseline and UXL-enabled configurations.
2. Correctness is verified before performance is compared, including tool results, retrieval quality, structured outputs, and final-task success.
3. At least one UXL integration improves a declared end-to-end metric on representative hardware without regressing task success.
4. A Python developer can install and run the winning integration in ten minutes or less from a clean environment.
5. Each proposed API or spec extension is backed by a measured bottleneck and a maintainer-approved ownership decision.
6. The catalog contains realistic skills and Harbor tasks that teach agents to adopt, debug, and validate the supported path.

## Workstreams

### 1. Reference workload and benchmark contract

Owner: cross-project agentic working group, with `uxl-performance-validation` maintainers.

Deliver a versioned workload that records:

- task-success and structured-output correctness;
- end-to-end latency and latency by pipeline stage;
- time-to-first-token and per-turn latency;
- retrieval quality and routing decisions;
- tool concurrency, queueing, and CPU utilization;
- accelerator utilization, transfers, and synchronization;
- install size, setup time, and dependency count.

Use at least three workload shapes: short interactive turns, tool-heavy fan-out, and retrieval-heavy long-horizon memory. Report p50 and p95 latency, throughput where relevant, and cost per verified success. Do not publish a speedup unless the baseline, environment, correctness checks, warmup, repetitions, and measurement boundaries are recorded.

### 2. Python-native scheduling pilot

Owner: oneTBB maintainers with one Python-agent-framework partner.

- Prototype a TBB-backed executor for parallel tool calls and irregular task DAGs.
- Target free-threaded CPython while documenting behavior on conventional CPython.
- Preserve cancellation, exceptions, context propagation, backpressure, and deterministic test behavior.
- Integrate with one existing framework through its executor or node-runtime extension point.
- Compare against the framework default and a standard Python executor on the same workload.

Exit gate: a pip-installable pilot demonstrates a repeatable end-to-end or tool-stage improvement with no task-success regression.

### 3. Retrieval and routing pilot

Owner: oneDAL maintainers with oneDPL/oneMath consultation where data movement or kernels cross ownership boundaries.

- Establish brute-force vector retrieval and lightweight routing baselines first.
- Measure conversion costs at Python, table, and device boundaries.
- Evaluate whether existing k-NN and clustering APIs are sufficient before proposing ANN support.
- Provide one framework-facing adapter and one standalone benchmark.

Exit gate: the pilot improves latency, throughput, or resource use at equivalent retrieval quality, with packaging and conversion costs included.

### 4. Agentic inference-shape characterization

Owner: oneDNN and oneMath maintainers.

- Define a shared shape corpus for short incremental prefill, batch-one decode, INT4/INT8 GEMV, and paged or non-contiguous KV access.
- Measure current implementations before setting optimization targets.
- Separate framework overhead, reorder and layout costs, dispatch overhead, and kernel time.
- Turn confirmed gaps into project issues with benchmark fixtures and acceptance thresholds.

Exit gate: maintainers approve a prioritized kernel backlog based on end-to-end sensitivity, not peak-kernel opportunity alone.

### 5. Structured parsing, tokenization, and KV discovery

Owner: agentic working group; final owners determined by the discovery record.

These are discovery tracks, not pre-approved UXL specifications.

- Profile tokenization, grammar-constrained parsing, schema validation, and cross-turn KV operations in the reference workload.
- Inventory mature open-source implementations and framework contracts.
- Define portability and interoperability gaps that UXL could uniquely solve.
- Produce a build/partner/adopt recommendation for each area.

Exit gate: steering committee decision backed by profiles, user interviews, ecosystem overlap, proposed ownership, and a reference API sketch. No spec work begins without this gate.

### 6. Multi-agent communication decision

Owner: oneCCL maintainers with actor/runtime experts.

- Benchmark only concrete use cases: shared-prefix broadcast, rollout-to-learner traffic, and sparse agent messages.
- Compare oneCCL transport capabilities with established message and actor systems.
- Decide whether to extend oneCCL, add a thin adapter, or explicitly keep agent messaging out of scope.

Exit gate: a documented positioning decision; absence of a new API is an acceptable result.

### 7. Packaging and developer experience

Owner: release/packaging representatives from participating projects.

- Define a clean-environment install test and a ten-minute first-result test.
- Prefer per-library packages and optional extras over a monolithic toolchain dependency.
- Publish supported platform, Python, backend, and hardware matrices.
- Make diagnostics report the selected device, backend, library versions, and fallback path.

Exit gate: CI proves installation and the reference example on each declared supported configuration.

## Two-quarter roadmap

### Quarter 1: measure, choose, and prototype

**Month 1 — charter and baseline**

- Form the working group and name one directly responsible individual per workstream.
- Freeze the reference workload, correctness contract, baseline implementations, and measurement schema.
- Add an `agentic-pipeline` suite to the Harbor capability model.
- Record clean-environment install and run baselines.

**Month 2 — bottleneck characterization**

- Profile the five pipeline stages on representative CPU and accelerator systems.
- Publish the agentic inference-shape corpus and first baseline results.
- Select oneTBB scheduling and oneDAL retrieval/routing pilots using measured contribution to end-to-end latency.
- Open discovery records for parsing, tokenization, KV management, and multi-agent messaging.

**Month 3 — integration prototypes**

- Produce pip-installable scheduling and retrieval prototypes.
- Land one framework integration for each selected pilot.
- Add with/without-UXL Harbor tasks and negative controls.
- Hold the first evidence review; stop or redirect pilots that do not move an end-to-end metric.

### Quarter 2: harden, validate, and decide

**Month 4 — correctness and portability**

- Exercise cancellations, failures, fallbacks, data conversion, synchronization, and mixed hardware.
- Run matched baseline, previous, and candidate trials with retained artifacts.
- Validate install flows on declared platforms and hardware.

**Month 5 — optimization and packaging**

- Optimize only the bottlenecks confirmed by the reference workload.
- Reduce installation and integration friction.
- Draft project-owned skills, examples, and troubleshooting guidance for the supported paths.
- Prepare spec proposals only for discovery tracks that passed their exit gates.

**Month 6 — adoption proof and steering decisions**

- Publish a reproducible report with correctness, latency, utilization, setup time, and cost per verified success.
- Submit framework integration changes upstream where appropriate.
- Ask maintainers to accept, revise, or reject each ownership and API proposal.
- Promote catalog skills only when the repository's maintainer-review and forward-test requirements are met.

## Program scorecard

Review this scorecard monthly. Targets are set after Month 1 baselines; before then, use `TBD`, not aspirational speedup numbers.

| Dimension | Metric | Gate |
| --- | --- | --- |
| Correctness | verified task-success rate | no regression versus baseline |
| Performance | p50/p95 end-to-end and per-stage latency | statistically repeatable improvement on a declared workload |
| Efficiency | total tokens, CPU time, accelerator time, and cost per verified success | improvement or explained tradeoff |
| Retrieval | recall/quality at fixed latency, and latency at fixed quality | parity on the controlled dimension |
| Reliability | cancellation, exception, fallback, and repeated-run success | all required scenarios pass |
| Developer experience | clean install to first verified result | at most 10 minutes |
| Portability | declared configurations passing in CI or self-hosted runners | evidence for every support claim |
| Adoption | upstream integrations, external evaluators, and retained users | target set after pilot partner commitment |

## Governance and decision rights

- The working group owns the reference workload, cross-project benchmark contract, and integration backlog.
- Project maintainers own changes to their libraries, APIs, packaging, and project-local skills.
- The steering committee decides cross-project specification scope and resolves ambiguous ownership.
- Performance claims require review under the existing correctness-gated validation policy.
- A pilot can be stopped at any monthly review when it lacks end-to-end relevance, a credible integration path, or a willing owner.

## Repository execution backlog

The current catalog already supplies the evaluation and promotion machinery. Extend it in this order:

1. Add a cross-project `uxl-agentic-pipeline` skill only after the reference workload and supported integration path exist; avoid a speculative umbrella skill.
2. Add an `agentic-pipeline` Harbor suite with baseline and UXL-enabled tasks, including a negative control.
3. Extend existing skill evals with agentic scenarios:
   - oneTBB: parallel tool fan-out, cancellation, blocking tools, and oversubscription;
   - oneDAL: retrieval quality, Python conversion cost, routing, and memory compaction;
   - oneDNN/oneMath: short-prefill, batch-one decode, quantized GEMV, layout, and dispatch overhead;
   - oneCCL: shared-prefix broadcast and a decision task distinguishing collectives from sparse messaging;
   - SYCL/performance: device fallback, launch overhead, transfer boundaries, and end-to-end claim repair.
4. Record maintainer incidents and upstream regressions as the preferred source for executable tasks.
5. Update `skills.yaml` and skill cards only when scope, sources, limitations, and evidence change together.

## Immediate steering asks

1. Approve a six-month agentic working group with named oneTBB, oneDAL, oneDNN/oneMath, oneCCL, packaging, and framework representatives.
2. Approve the reference-workload-first strategy and require measured bottlenecks before specification work.
3. Select one Python agent framework and two representative hardware environments for the pilot.
4. Commit maintainers to a monthly evidence review and Month 6 ownership decisions.
