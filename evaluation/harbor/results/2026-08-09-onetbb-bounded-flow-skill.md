# oneTBB bounded-flow skill iteration: 2026-08-09

This experiment tests a targeted `uxl-onetbb` revision against the hard `onetbb-bounded-image-flow-graph` task. The candidate adds general guidance for bounded admission, explicit `function_node` stage limits, exactly-once capacity return, bounded asynchronous I/O, nested-runtime budgeting, and resource validation. The evaluator task and its expected concepts were unchanged during the model trials.

## Three-arm Harbor run

Each arm used three serial attempts with the same task, agent, model, and reasoning effort. All nine trials completed without exceptions.

| Arm | Raw mean reward | Trial rewards | Cost (USD) | Runtime |
| --- | ---: | --- | ---: | ---: |
| No skill | 0.5556 | 0.3056, 0.6667, 0.6944 | $0.529507 | 6m 41s |
| Previous skill (`main`) | 0.7963 | 0.7778, 0.8056, 0.8056 | $0.973446 | 9m 07s |
| Candidate skill | 0.8148 | 0.7778, 0.7778, 0.8889 | $0.826298 | 6m 57s |

The raw verifier showed the intended repair improvement: candidate repair rose from 0.8333 to 1.0000. However, the candidate validation mean fell from 0.6667 to 0.4444 even though the artifacts contained serial baselines, per-input or admission identity, released ownership, live-resource counters, bounded queued counts, RSS, and thread evidence.

## Verifier audit

The validation false negatives came from phrase-level brittleness rather than missing concepts. The rubric required narrow forms such as `serial baseline`, singular `message ID`, and `queue depth`. It rejected equivalent phrases including `serial small-data baseline`, `exactly one output or error per input`, `admission IDs`, `live jobs`, and `queued counts`.

The audited rubric now accepts those equivalent operational forms while preserving the same three-part contracts:

- compare against a serial reference or baseline;
- prove item identity and released ownership or lifetime;
- measure memory, queued or in-flight resources, and runtime threads or utilization.

A regression test covers the equivalent wording. No agent artifact, task prompt, or expected solution was changed. Re-scoring the nine saved artifacts with the audited deterministic verifier gives:

| Arm | Diagnosis | Repair | Validation | Audited mean reward | Perfect trials |
| --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.7778 | 0.6667 | 0.3333 | 0.5926 | 0/3 |
| Previous skill | 0.8889 | 0.8333 | 0.8889 | 0.8704 | 1/3 |
| Candidate skill | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/3 |

## Decision

Retain the candidate skill change and the verifier correction. The candidate consistently closes the targeted stage-limit gap and produces complete bounded-flow diagnoses, repairs, and validation plans under the audited rubric. It improves audited mean reward by 0.1296 versus the previous skill and by 0.4074 versus no skill.

This remains a small, single-task experiment. It supports the bounded-flow guidance but does not establish broad oneTBB skill quality. The next generalization gate is an independent flow-graph task with different failure evidence and success phrasing; existing histogram and scan tasks remain regression coverage for unrelated oneTBB patterns.

## Validation and provenance

- Skill quick validation passed.
- Catalog and 26 eval definitions passed validation.
- Harbor suite validation passed: 8 skills, 49 planned tasks, 17 implemented.
- Generated capability matrix, answer checkers, and agent wrappers are current.
- Unit tests: 25 passed, including the new verifier regression test.
- Link check: 52 external links plus local links passed.
- Fresh audited oracle job: `onetbb-rubric-oracle-20260809-165108`, 1/1 trial, reward 1.0, zero exceptions.
- Comparison job prefix: `onetbb-bounded-flow-v1-20260809-162245`.
- Starting revision and previous reference: `main@6feb3f3`.
- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per arm: 3; concurrency: 1.

Raw job results remain in the ignored local `harbor-jobs` directory. The original result files retain the pre-audit scores for historical integrity; the audited scores above were computed read-only from the saved answer artifacts.
