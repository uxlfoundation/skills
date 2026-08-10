---
name: uxl-onetbb
description: "Use for oneAPI Threading Building Blocks (oneTBB) C++ parallelism work: selecting parallel_for, parallel_reduce, parallel_scan, parallel_pipeline, flow graph, task_group, task_arena, global_control, concurrent containers, scalable allocators, migration from legacy TBB, and diagnosing races, oversubscription, grainsize, affinity, or scheduler behavior."
---

# UXL oneTBB

## Purpose

Help an agent map CPU parallelism problems to composable oneTBB patterns while preserving correctness, determinism where required, and maintainable C++.

## First Pass

1. Classify the workload shape: independent loop, reduction, prefix scan, producer/consumer pipeline, dependency graph, recursive task tree, or shared container.
2. Identify mutable state, ordering requirements, exception behavior, blocking calls, and existing thread pools.
3. Read nearby concurrency code before introducing a new abstraction.
4. Do not use oneTBB for GPU offload; use oneDPL/SYCL guidance instead.

## Pattern Selection

- Use `parallel_for` for independent iteration spaces.
- Use `parallel_reduce` when each partition can accumulate privately then combine.
- Use `parallel_scan` for prefix operations.
- Use `parallel_pipeline` for ordered streaming stages.
- Use flow graph for irregular dependencies, message passing, and bounded concurrency.
- Use `task_group` for explicit fork/join work.
- Use `task_arena` or `global_control` when integrating with existing runtimes or limiting parallelism.

## Bound Resource-Owning Flow Graphs

When messages retain buffers, handles, or other scarce resources across stages:

1. Bound admission before acquiring the expensive resource. Use a `limiter_node` threshold with feedback to `decrementer()`, or a rejecting-node/input-node pull pattern when upstream must stop producing. Handle rejected `try_put` calls; do not move the unbounded queue in front of the graph.
2. Give every `function_node` an explicit finite concurrency matched to its resource: for example, a small I/O-stage limit, a measured compute-stage limit, and a serial or device-appropriate sink limit. A finite concurrency value with the default queueing policy limits active body invocations but can still buffer accepted messages, so it does not replace a global in-flight bound.
3. Return capacity exactly once after ownership is released on success, failure, exception, and cancellation paths. Prefer one non-throwing terminal/error path or an RAII completion guard; do not connect only the successful edge to the decrementer.
4. Move blocking external work to a bounded executor through `async_node` when practical. Balance gateway reservations and releases on every callback path, and keep the graph alive until callbacks finish.
5. Treat outer-node concurrency, nested oneTBB work, arena size, and foreign thread pools as one runtime budget. Avoid many concurrent node bodies that each start an unconstrained nested `parallel_for`.
6. Validate the bound directly: track admissions, completions, live resources, queue depths, RSS, thread counts, throughput, and tail latency during long runs and injected failures.

## Implementation Workflow

1. Prove the serial behavior with a small test or existing baseline.
2. Make captured state explicit and prefer partition-local temporaries over shared mutation.
3. Choose grainsize only after estimating work per element and memory locality.
4. Add tests for race-prone behavior, ordering, cancellation, and exceptions.
5. Benchmark with realistic core counts and input sizes. Report thread limits and affinity if relevant.

## Tune Grain and Affinity from Evidence

1. Start with the default `auto_partitioner`. Add a minimum grainsize or serial cutoff only when completed-call measurements show scheduling overhead for the target body and input sizes. Sweep the body cost, problem size, grainsize, and concurrency; tiny chunks waste scheduling work, while coarse chunks can idle cores or worsen tails.
2. Use `affinity_partitioner` as a cache-affinity hint for repeated loops over the same or similarly mapped, cache-resident data. Retain the same partitioner object across those repetitions. Confirm benefit against cold/new-buffer and oversized working sets instead of treating affinity as a universal improvement.
3. Separate oneTBB task affinity from operating-system placement. An affinity partitioner does not pin threads or place NUMA pages. Record the effective CPU set, topology, arena concurrency, first-touch and memory placement, migrations, cache misses, bandwidth, and the oneTBB/build version. Apply `task_arena` constraints or external placement only when controlled comparisons justify them.
4. Gate every tuning result on a serial correctness reference, then report warmup, repetitions, median and tail latency, throughput, task/body counts, active-worker counts, CPU utilization, and the exact workload and placement where the choice wins.

## Gotchas

- A lambda that mutates shared state is not made safe by wrapping it in `parallel_for`.
- Too-small grainsize can lose to scheduling overhead; too-large grainsize can starve cores.
- Nested parallelism and foreign thread pools can oversubscribe unless controlled.
- Blocking I/O inside oneTBB tasks can harm scheduler behavior.
- Flow graph concurrency limits are part of correctness for resource-bound stages.

## Output Contract

When delivering oneTBB work, include:

- Selected oneTBB pattern and why alternatives were rejected.
- Shared-state and ordering analysis.
- Threading limits or arena assumptions.
- Admission, in-flight ownership, and capacity-return rules when resources cross stages.
- Correctness test and benchmark plan.
- Remaining race, determinism, or scheduling risks.

## References

Read [official sources](references/official-sources.md) for current oneTBB APIs, migration notes, and scheduler details.
