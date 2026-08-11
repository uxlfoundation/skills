# Performance cgroup-concurrency skill calibration: 2026-08-11

This calibration measures whether the new cgroup-aware oneTBB guidance in `uxl-performance-validation` improves a live, maintainer-sourced container-concurrency repair. All three treatments reached full reward, so the task cannot demonstrate a quality lift from the skill.

## Three-attempt calibration

Each arm used three serial attempts with the same committed task, model, reasoning effort, timeout, and two-CPU cgroup environment. All nine trials completed without exceptions.

| Arm | Mean reward | Verified successes | Uncached input | Cached input | Output | Total token burn | Tokens / success | Cost | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 3/3 | 40,291 | 228,096 | 6,929 | 275,316 | 91,772 | $0.523373 | 7m 53s |
| Previous skill | 1.0000 | 3/3 | 56,413 | 377,600 | 13,178 | 447,191 | 149,064 | $0.866205 | 11m 52s |
| Candidate skill | 1.0000 | 3/3 | 57,028 | 428,288 | 16,355 | 501,671 | 167,224 | $0.989934 | 12m 56s |

| Arm | Trial 1 total tokens | Trial 2 total tokens | Trial 3 total tokens |
| --- | ---: | ---: | ---: |
| No skill | 97,141 | 97,473 | 80,702 |
| Previous skill | 161,593 | 127,499 | 158,099 |
| Candidate skill | 164,586 | 183,931 | 153,154 |

Total token burn counts all input tokens once, including cached input, plus output tokens. Uncached input is reported separately as total input minus cached input.

## Trajectory audit

All nine agents implemented strict `cpu.max` parsing, preserved oneTBB execution and the deterministic checksum, exercised the live numeric quota, and handled fractional, unconstrained, missing, malformed, zero, extra-field, and overflow cases.

The no-skill agents completed the repair in three or four shell commands. Previous-skill agents used five to eight commands after reading the skill and its benchmark contract. Candidate-skill agents used six to twelve commands, performed broader environment inspection, and repeatedly reran live-quota checks. The extra validation produced more detailed evidence, but the binary verifier already captured the required behavior and awarded identical reward.

## Interpretation and decision

The candidate used 12.2% more total tokens, 14.3% more cost, and 9.0% more runtime than the previous skill. Against no skill, it used 82.2% more tokens, 89.2% more cost, and 64.1% more runtime. Quality was identical in every arm.

Classify `performance-cgroup-concurrency-quota` as `ceiling` and retain it as deterministic smoke/regression coverage. Keep the concise cgroup-versus-affinity guidance because it captures real domain knowledge, but do not use this task as evidence that the performance skill improves quality or token efficiency. The task prompt specifies the repair contract and edge cases precisely enough that a strong model does not need the skill.

The next skill-value task should leave diagnosis and evidence selection open while keeping the verifier deterministic. It should reward earlier identification of a project-specific workflow or signal rather than restating the repair algorithm in the prompt.

## Provenance

- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per arm: 3; concurrency: 1.
- Task revision: `01ab1a4b65cf550a0cb8daf29be05d0940d60774`.
- Previous skill: `f6d85a657399a53a26b074946afb3dbf38421f59`.
- Candidate skill tree: `dcb8ba0e5be0ee74281353982960ef11c3cbbcd6`.
- Job prefix: `performance-cgroup-calibration-20260811`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/performance-cgroup-calibration-20260811-noskill)
- [Previous skill](http://127.0.0.1:8080/jobs/performance-cgroup-calibration-20260811-previous)
- [Candidate skill](http://127.0.0.1:8080/jobs/performance-cgroup-calibration-20260811-candidate)
