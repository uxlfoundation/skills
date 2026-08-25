# Harbor skill comparison: `uxl-sycl-build-debug`

Task: `sycl-compile-time-backend-link`

## Outcome

- **NO QUALITY CHANGE: reward changed by +0.0000**
- Candidate versus no skill: +0.0000 reward.
- Candidate versus previous: +0.0000 reward, -2.3% cost.
- Quality gate at reward `1.0000`: candidate 1/1, previous 1/1.
- Efficiency: candidate tokens per verified success changed by -2.1%; candidate cost per verified success changed by -2.3%.
- Reliability: all runs completed without errors.
- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value.

## Results

| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | [`sycl-link-calibration-20260816-noskill`](http://127.0.0.1:8080/jobs/sycl-link-calibration-20260816-noskill) | 1.0000 | 1/1 | 0 | 1.0000x1 | 23,324 | 245,248 | 2,427 | $0.312054 | 2m 36s |
| Previous | [`sycl-link-calibration-20260816-previous`](http://127.0.0.1:8080/jobs/sycl-link-calibration-20260816-previous) | 1.0000 | 1/1 | 0 | 1.0000x1 | 32,171 | 216,576 | 2,519 | $0.344713 | 2m 32s |
| Candidate | [`sycl-link-calibration-20260816-candidate`](http://127.0.0.1:8080/jobs/sycl-link-calibration-20260816-candidate) | 1.0000 | 1/1 | 0 | 1.0000x1 | 29,683 | 213,504 | 2,718 | $0.336707 | 2m 34s |

## Verified-success efficiency

Quality gate: trial reward at least `1.0000`.

| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 270,999 | 270,999 | $0.312054 |
| Previous | 1/1 | 251,266 | 251,266 | $0.344713 |
| Candidate | 1/1 | 245,905 | 245,905 | $0.336707 |

## Metric breakdown

| Metric | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| `device_count` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |
| `hidden_cases` | 4.0000 | 4.0000 | 4.0000 | +0.0000 |
| `reward` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |

## Provenance

- Task: `working-tree@3feb34b0ee30fe1796d48e349fc592c60a3a69b7 (content sha256 daefc2a5d33f7641a85a19e3e1deecf8ea0b5a15d69f61d16c559c2bea52bbc3; tree 8b79c88bfa28e15d6dd5b8cbf50b88c3ca3d2101)`
- Previous skill: `main@ce5f7b0548e77ea54609e8d5d2be772986a90962 (tree 5ed42597a880146e64fffcffbbe1c051ecd6fbdc)`
- Candidate skill: `working-tree@3feb34b0ee30fe1796d48e349fc592c60a3a69b7 (content sha256 8ccee7a08840f9da2958c79f0b4232d2fd7bb6df430951f7adf99a3ff904bb3a; tree 5ed42597a880146e64fffcffbbe1c051ecd6fbdc)`
- Agent/model: `codex` / `gpt-5.6-sol`
- Attempts per arm: `1`
- Verified reward floor: `1.0000`
- No-skill result: `harbor-jobs/sycl-link-calibration-20260816-noskill/result.json`
- Previous result: `harbor-jobs/sycl-link-calibration-20260816-previous/result.json`
- Candidate result: `harbor-jobs/sycl-link-calibration-20260816-candidate/result.json`

Review any changed or failed trial in Harbor: inspect **Verifier** for the score, **Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.

## Portfolio classification

All three artifacts made the same valid repair and supplied appropriate link-phase and device evidence. The previous and candidate skill trees are identical, so their 2.1% token difference is run-to-run variation rather than a skill change.

Candidate total token burn was 9.3% lower than no skill (245,905 versus 270,999), but candidate cost was 7.9% higher ($0.336707 versus $0.312054) because the token mix differed. With one attempt per arm, this is a directional efficiency observation, not promotion evidence.

The task is classified as `smoke` / `ceiling`: it protects a real compiler, linker, runtime, and CPU-device path, but does not measure incremental skill quality for this model. Its discriminating replacement is the harder hardware-agnostic `sycl-transitive-target-link-contract` task; the redundant planned target-device environment report is removed from the v1 portfolio.
