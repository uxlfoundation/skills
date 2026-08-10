# oneTBB failure-flow generalization probe: 2026-08-10

This wave implements the planned `onetbb-cancellation-exception-propagation` task as an executable multi-stage flow graph. The task checks bounded scratch ownership across stages, per-job transform and persist failures, exactly one ordered outcome per input, zero leaked ownership, continued progress, and useful parallelism.

## Fixture calibration

| Fixture | Reward | Meaning |
| --- | ---: | --- |
| Oracle | 1.0000 | Correct implementation compiles and passes all hidden cases. |
| Misleading starter | 0.0000 | Unbounded admission and escaping stage exceptions are rejected. |

The fresh Harbor oracle job was `onetbb-failure-flow-oracle-20260810-101308`. The starter was evaluated with the same compiled verifier in the task container.

## Blind probe and verifier audit

One matched attempt was run for no skill, the previous `main` skill, and the bounded-flow candidate. The initial raw result was 0/0/1. Before advancing to three-attempt calibration, the failed artifacts were audited.

Both failed artifacts were substantively correct. They used a `queue_node` for lightweight pending descriptors, a `limiter_node` across the scratch-owning lifetime, completion feedback to the decrementer, per-job failure conversion, and ordered outcomes. They declared downstream `function_node`s as `unlimited`, but the global limiter still bounded all active scratch-owning work to `capacity`. The verifier had incorrectly required the oracle's exact `input_node` syntax and rejected the word `unlimited` even when behavioral limits held.

The audited verifier retains the architectural and behavioral requirements—flow graph, limiter, completion feedback, bounded live scratch, complete outcomes, failure isolation, and observed parallelism—but accepts both valid source/pull and lightweight-queue admission implementations. The oracle now uses the alternative queueing form so CI continuously protects that implementation freedom.

Re-running the saved artifacts with the audited verifier gives:

| Arm | Audited reward | Classification |
| --- | ---: | --- |
| No skill | 1.0000 | Ceiling |
| Previous skill | 1.0000 | Ceiling |
| Candidate skill | 1.0000 | Ceiling |

No three-attempt calibration was run because the audited probe has no headroom. The original Harbor job files retain their raw 0/0/1 scores for historical integrity. The probe job prefix is `onetbb-failure-flow-probe-20260810-101906`.

## Portfolio decision

Retain the task as executable smoke coverage and classify it `ceiling`. It raises implemented portfolio coverage from 17 to 18 of 49 tasks and oneTBB coverage from 3 to 4 of 7 planned tasks, but it does not add a second discriminating oneTBB task.

The next oneTBB gate should use less-prescriptive evidence and require diagnosis across runtime composition or performance behavior rather than restating the complete repair contract. The planned nested-thread-pool arena or grainsize/affinity tasks are better candidates.

## Validation and provenance

- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per arm: 1; concurrency: 1.
- Task revision: `882c609` plus the audited verifier changes recorded with this report.
- Skill candidate revision: `ac3f551`.
- Previous skill reference: `main@6feb3f3`.
- All four probe jobs completed without Harbor exceptions.
