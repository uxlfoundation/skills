# Agentic reference workload

This directory contains the versioned, framework-neutral benchmark contract for UXL's agentic proof point. Version 1 is intentionally deterministic and dependency-free: it fixes tool outputs, retrieval inputs, structured answers, cancellation behavior, and timing boundaries before a framework or UXL optimization is introduced.

It measures orchestration and retrieval plumbing. It does **not** simulate model quality, claim inference performance, or represent any executor as a UXL implementation.

## Workload shapes

- `short-turn`: one retrieval decision and one tool result.
- `tool-fan-out`: four independent, waitable tool calls that preserve result identity.
- `retrieval-heavy`: repeated lexical retrieval over a fixed corpus and six fixed queries.

Every timed attempt must pass exact route and structured-answer checks. Separate controls verify pre-cancellation and exception identity.

## Run the baseline

From the repository root:

```powershell
python -m evaluation.agentic.reference_workload --executor serial --warmups 1 --repetitions 5 --summary-only
python -m evaluation.agentic.reference_workload --executor threaded --max-workers 4 --warmups 1 --repetitions 5 --summary-only
```

Retain a full report with `--output <path>`. The report records raw attempts, stage-level monotonic timings, environment information, and failure-path checks.

## Fixed measurement boundaries

- `plan`: validate and materialize the scenario's queries and calls.
- `retrieval`: execute the fixed retrieval passes and select document IDs.
- `tool_execution`: dispatch calls and collect identified results.
- `synthesis`: build the exact expected structured answer.
- `end_to_end`: all four stages, including executor overhead.

Report p50 and p95 from repeated, correctness-passing attempts. Compare executors only on the same commit, environment, warmup, repetition count, and workload contract. The fixture's millisecond waits represent waitable external tools; they are not a CPU-kernel benchmark.

## Extension contract

A framework adapter should implement the `Executor.run` protocol in `benchmark.py`, preserve cancellation and `ToolExecutionError.call_id`, and return `ToolResult` records. A UXL candidate remains a candidate until it is measured against both the serial baseline and the framework's normal executor. Do not add an umbrella `uxl-agentic-pipeline` skill until a supported integration passes this contract.

## First framework adapter: LangGraph

Install the pinned optional dependency, then run the same contract through LangGraph's Functional API:

```powershell
python -m pip install -r evaluation/agentic/requirements-langgraph.txt
python -m evaluation.agentic.reference_workload --executor langgraph --max-workers 4 --warmups 1 --repetitions 5 --summary-only
```

This adapter is a framework baseline, not a UXL-accelerated executor. It uses LangGraph's normal task runtime and preserves the workload's exact output, cancellation, and exception checks.

## First UXL candidate: oneDAL retrieval

The optional oneDAL prototype converts the fixed corpus and queries to binary bag-of-words vectors and performs exact brute-force nearest-neighbor search. Setup time and per-query conversion remain visible in the report.

```powershell
python -m pip install -r evaluation/agentic/requirements-onedal.txt
python -m evaluation.agentic.reference_workload --executor langgraph --retriever onedal --max-workers 4 --warmups 1 --repetitions 5 --summary-only
```

This small fixture proves the adapter and correctness contract; it is not a representative vector-search performance claim. A go decision requires a larger quality-scored corpus, matched retrieval quality, conversion-inclusive timing, and at least one additional hardware/platform lane.
