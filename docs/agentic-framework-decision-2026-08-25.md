# First agent-framework decision — 2026-08-25

Decision: use LangGraph as the first framework integration target, while keeping the benchmark contract framework-neutral.

## Selection criteria

The first target needs a stable Python API, deterministic non-model nodes, native fan-out/fan-in, bounded concurrency, clear failure behavior, permissive licensing, and a small optional install. It must let us compare UXL candidates with the framework's normal execution path rather than replacing the framework.

## Candidates

| Framework | Fit | Current concern | Decision |
| --- | --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Graph nodes can be ordinary Python functions; the Graph and Functional APIs support parallel execution, dynamic workers, concurrency limits, and explicit failure semantics. MIT licensed. | Its existing parallel runtime is already a strong baseline; a oneTBB pilot must beat or materially improve it, not a serial straw baseline. | Selected. |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | Strong typed outputs and eval tooling; its graph beta includes fork/join concepts. MIT licensed. | The relevant graph API is still explicitly beta, increasing adapter churn for the first proof point. | Revisit after the first contract is stable. |
| [AutoGen](https://github.com/microsoft/autogen) | Mature agent and distributed-runtime concepts with parallel tool calls and GraphFlow. | GraphFlow is documented as experimental, and stateful agent tools have parallel-execution restrictions. | Keep as a portability target, not the first adapter. |

## Evidence from the frozen workload

Five local, correctness-passing attempts on GLOW (CPython 3.13.13, Windows 11, 28 logical CPUs) show two distinct bottlenecks. Exact retained summaries live under `evaluation/agentic/results/`.

- Tool fan-out: serial p50 71.76 ms; standard threaded p50 23.15 ms; LangGraph p50 37.85 ms.
- Retrieval-heavy: serial lexical p50 38.57 ms, of which 38.56 ms is the retrieval stage; switching executors does not materially change it.
- Short-turn: the threaded baseline is slower than serial at this tiny scale, so the suite supplies a built-in negative control against unconditional parallelization.

These fixtures deliberately use deterministic waitable tools and lexical retrieval. The numbers select where to prototype; they are not UXL performance results and do not generalize to production agents.

## Pilot decision

Prototype the LangGraph adapter first and measure its normal runtime. Do not yet implement a oneTBB-backed runtime: the standard threaded baseline already removes most waitable fan-out time, so a credible oneTBB proposal needs a CPU-heavy or irregular DAG case, cancellation/backpressure value, free-threaded CPython evidence, or a developer-experience advantage.

The first oneDAL adapter is now implemented as exact brute-force nearest-neighbor retrieval over deterministic bag-of-words vectors. It preserves every expected route, but this fixture is a performance **no-go**: LangGraph plus lexical retrieval has a 39.25 ms retrieval-heavy p50, while LangGraph plus oneDAL takes 50.04 ms and adds 7.89 ms of setup. The small corpus cannot amortize conversion and dispatch overhead.

Retain the prototype as a correctness and integration fixture. Do not optimize it or claim a benefit. A new oneDAL go decision requires a larger quality-scored vector corpus, matched quality, conversion-inclusive timing, and an additional platform lane. The go/no-go measurement remains end-to-end verified success, not kernel time.

## Compatibility record

- Adapter target: `langgraph==1.2.11`
- Adapter surface: Functional API `@task` plus `@entrypoint`
- First UXL candidate: `scikit-learn-intelex==2026.1.0`, direct `onedal.neighbors.NearestNeighbors`
- Model/network calls: none
- Required contract behavior: exact results, result identity, pre-cancellation, exception identity, p50/p95 stage timings
- CI: a separate optional-dependency job installs the pin and runs the reference contract
- Current result: adapter correctness passes; current small-corpus performance gate fails, so no UXL speedup is claimed

Re-evaluate the pin and this decision when the adapter surface changes, the workload adds a real model, or another framework partner commits to the pilot.
