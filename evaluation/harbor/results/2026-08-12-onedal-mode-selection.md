# oneDAL computation-mode selection task

Date: 2026-08-12

## Purpose

Add hardware-agnostic coverage for a common oneDAL architecture error: treating online or distributed computation as an automatically faster version of batch. The task asks an agent to select a mode from data arrival, memory, partitioning, and launch evidence, then define correctness and end-to-end measurement gates.

## Source basis

- The [oneDAL computational-modes guide](https://uxlfoundation.github.io/oneDAL/onedal/programming-model/computational-modes.html) defines batch over the entire data set, online over streamed blocks with partial-result finalization, and distributed over data spread across devices or compute nodes.
- The [oneDAL SPMD guide](https://uxlfoundation.github.io/oneDAL/onedal/spmd/index.html) documents the communicator-based distributed programming model.
- Exact mode availability remains algorithm-, interface-, version-, and device-specific; the skill requires checking that support rather than assuming it.

## Verifier design

The grouped rubric checks four independent areas:

1. The workload evidence that makes batch, online, or distributed appropriate.
2. Algorithm/interface/device support plus data and runtime topology evidence.
3. Batch-reference parity, chunk invariants, and multi-rank partition/collective invariants.
4. Conversion- and communication-aware end-to-end measurement with a bounded recommendation.

Unsupported “always faster” claims zero the reward. The verifier does not require one exact answer or code sample.

## Acceptance evidence

- Harbor `0.20.0` oracle job: `harbor-jobs/onedal-mode-oracle-20260812`
- Trials: 1 completed, 0 exceptions
- Combined reward: `1.0`
- Empty answer probe: `0.0`
- Generic mode/performance keyword probe: `0.0`
- Unsupported always-faster claim probe: `0.0`
- Portfolio validation after addition: 8 skills, 49 planned tasks, 25 implemented

## Interpretation and limit

This is a review/answer-quality task. It tests whether a skill guides a sound mode decision on free hosted runners, but it does not count as live oneDAL reproduction or end-to-end triage. The next oneDAL milestone should execute an actual CPU workload and verify data-layout or metric parity behavior.
