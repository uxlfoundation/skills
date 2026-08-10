# oneTBB grainsize/affinity skill iteration: 2026-08-10

This wave implements `onetbb-grainsize-affinity-regression`, an evidence-driven answer-quality task. The agent receives a cheap stencil loop forced into grainsize-1 `simple_partitioner` chunks, a controlled benchmark matrix, and deployment/topology notes. A complete review must separate scheduling granularity, cache-affinity hints, and operating-system/NUMA placement; propose bounded repairs; and design correctness-gated experiments instead of declaring one universal configuration.

## Fixture calibration

| Fixture | Reward | Meaning |
| --- | ---: | --- |
| Oracle | 1.0000 | All diagnosis, repair, validation, and claim-safety criteria pass. |
| Empty answer | 0.0000 | Missing work is rejected. |

The initial Harbor oracle job was `onetbb-grainsize-affinity-oracle-20260810-120422`. The fresh final-rubric job `onetbb-grainsize-affinity-oracle-final-20260810-125404` also scored 1.0000 with zero exceptions.

## Skill iteration and verifier audit

The candidate adds a concise workflow that starts from automatic chunking, measures serial cutoffs and grainsize/body-cost crossovers, qualifies persistent `affinity_partitioner` use by reuse and cache fit, separates task affinity from OS/NUMA placement, and records scheduler/locality evidence.

The initial one-attempt three-arm probe produced raw rewards 0.8056/0.8056/0.8333 for no skill, previous skill, and candidate. Artifact audit found equivalent operational wording that the first rubric did not accept, including “default automatic partitioning,” “serial path,” “serial oracle,” and “body/task calls.” Uniform re-scoring gave 0.9167 for all three, correctly showing that candidate revision 1 had no substantive lift because every artifact omitted active-worker or CPU-utilization evidence.

The workflow was then amended to require active-worker counts and CPU utilization. A focused candidate-v2 job (`onetbb-grainsize-affinity-candidate-v2-20260810-122003`) contained the missing scheduler/locality evidence and audited to 1.0000. Regression tests now protect the implementation-neutral alternatives used by saved artifacts. Raw Harbor result files retain their original scores for historical integrity.

## Three-attempt calibration

Each arm used three serial attempts with the same task, model, reasoning effort, and concurrency. All nine trials completed without exceptions. The job prefix was `onetbb-grainsize-affinity-calibration-20260810-122440`.

| Arm | Raw mean | Raw rewards | Audited mean | Audited rewards |
| --- | ---: | --- | ---: | --- |
| No skill | 0.6018 | 0.5833, 0.5833, 0.6389 | 0.7407 | 0.6944, 0.7222, 0.8056 |
| Previous skill (`main`) | 0.7408 | 0.6111, 0.8056, 0.8056 | 0.8056 | 0.6944, 0.8056, 0.9167 |
| Candidate skill | 0.8241 | 0.5833, 0.8889, 1.0000 | 0.9630 | 0.8889, 1.0000, 1.0000 |

| Audited component | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0.7778 | 0.7778 | 0.8889 | +0.1111 |
| Repair | 0.7778 | 0.8889 | 1.0000 | +0.1111 |
| Validation | 0.6667 | 0.7500 | 1.0000 | +0.2500 |
| Combined reward | 0.7407 | 0.8056 | 0.9630 | +0.1574 |

The candidate improves audited mean by 0.1574 over the previous skill and 0.2223 over no skill. Two candidate attempts are complete; the third omits the substantive coarse-grain starvation/tail-risk concept and remains at 0.8889. The audit did not erase that variance.

## Decision

Retain the candidate skill workflow and classify the task `headroom`. It becomes the second calibrated discriminating oneTBB task, while the executable histogram, scan, failure-flow, and runtime-composition tasks remain regression/smoke coverage.

The portfolio now implements 20 of 49 tasks and 6 of 7 planned oneTBB tasks. The remaining oneTBB task is the planned legacy-API migration smoke case; broader progress should next shift to suites with only one implemented task.

## Provenance and validation

- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per calibration arm: 3; concurrency: 1.
- Previous skill: `main@ce5f7b0`.
- Task and candidate calibration revision: `d5f472e` plus the audited rubric alternatives recorded with this report.
- Raw calibration cost: $0.615867 no skill, $0.968529 previous, and $0.873919 candidate.
- Raw calibration runtime: 7m 05s, 8m 22s, and 7m 44s respectively.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onetbb-grainsize-affinity-calibration-20260810-122440-noskill)
- [Previous skill](http://127.0.0.1:8080/jobs/onetbb-grainsize-affinity-calibration-20260810-122440-previous)
- [Candidate skill](http://127.0.0.1:8080/jobs/onetbb-grainsize-affinity-calibration-20260810-122440-candidate)

The tuning contract follows oneTBB's documented automatic/simple chunking behavior and its conditional cache-affinity model. See the [partitioner summary](https://uxlfoundation.github.io/oneTBB/main/tbb_userguide/Partitioner_Summary.html), [chunking guidance](https://uxlfoundation.github.io/oneTBB/main/tbb_userguide/Controlling_Chunking_os.html), and [cache-affinity guidance](https://uxlfoundation.github.io/oneTBB/main/tbb_userguide/Bandwidth_and_Cache_Affinity_os.html).
