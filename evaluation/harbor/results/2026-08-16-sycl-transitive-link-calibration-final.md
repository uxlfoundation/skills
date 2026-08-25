# Harbor skill comparison: `uxl-sycl-build-debug`

Task: `sycl-transitive-target-link-contract`

## Outcome

- **NO QUALITY CHANGE: reward changed by +0.0000**
- Candidate versus no skill: +0.0000 reward.
- Candidate versus previous: +0.0000 reward, -3.4% cost.
- Quality gate at reward `1.0000`: candidate 3/3, previous 3/3.
- Efficiency: candidate tokens per verified success changed by -8.0%; candidate cost per verified success changed by -3.4%.
- Reliability: all runs completed without errors.
- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value.

## Results

| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | [`sycl-transitive-calibration-20260816-r2-noskill`](http://127.0.0.1:8080/jobs/sycl-transitive-calibration-20260816-r2-noskill) | 1.0000 | 3/3 | 0 | 1.0000x3 | 91,086 | 598,272 | 8,941 | $1.022796 | 3m 38s |
| Previous | [`sycl-transitive-calibration-20260816-r2-previous`](http://127.0.0.1:8080/jobs/sycl-transitive-calibration-20260816-r2-previous) | 1.0000 | 3/3 | 0 | 1.0000x3 | 89,777 | 714,496 | 13,866 | $1.222113 | 4m 12s |
| Candidate | [`sycl-transitive-calibration-20260816-r4-candidate`](http://127.0.0.1:8080/jobs/sycl-transitive-calibration-20260816-r4-candidate) | 1.0000 | 3/3 | 0 | 1.0000x3 | 105,611 | 636,160 | 11,162 | $1.180995 | 10m 29s |

## Verified-success efficiency

Quality gate: trial reward at least `1.0000`.

| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |
| --- | ---: | ---: | ---: | ---: |
| No skill | 3/3 | 698,299 | 232,766 | $0.340932 |
| Previous | 3/3 | 818,139 | 272,713 | $0.407371 |
| Candidate | 3/3 | 752,933 | 250,978 | $0.393665 |

## Metric breakdown

| Metric | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| `device_count` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |
| `hidden_cases` | 4.0000 | 4.0000 | 4.0000 | +0.0000 |
| `reward` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |

## Provenance

- Task: `c617f4b (task tree d211a34)`
- Previous skill: `main@ce5f7b0 (tree 5ed4259)`
- Candidate skill: `c617f4b (tree 5ed4259; identical skill content)`
- Agent/model: `codex` / `gpt-5.6-sol`
- Attempts per arm: `3`
- Verified reward floor: `1.0000`
- No-skill result: `harbor-jobs/sycl-transitive-calibration-20260816-r2-noskill/result.json`
- Previous result: `harbor-jobs/sycl-transitive-calibration-20260816-r2-previous/result.json`
- Candidate result: `harbor-jobs/sycl-transitive-calibration-20260816-r4-candidate/result.json`

Review any changed or failed trial in Harbor: inspect **Verifier** for the score, **Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.

## Portfolio classification

All nine included trials passed, and artifact review confirmed target-scoped repairs with correct link-phase and runtime evidence. The previous and candidate skill trees are identical; their 8.0% aggregate token difference is run variation, not a skill revision.

Against no skill, the candidate used 7.8% more tokens per verified success (250,978 versus 232,766) and cost 15.5% more ($0.393665 versus $0.340932) at identical quality. The task is classified as `smoke` / `ceiling`; it protects an authentic CMake/compiler/linker/runtime path but does not demonstrate incremental skill value for this model.

Excluded infrastructure attempts are preserved but do not enter the table:

- `sycl-transitive-calibration-20260816-r2-candidate`: all three agents exited when concurrent writable layers exhausted the Docker Desktop VHD and its metadata database returned I/O errors.
- `sycl-transitive-calibration-20260816-r3-candidate`: all three rewards were `1.0`, but direct native execution omitted `PYTHONUTF8=1`, so Harbor could not decode Codex events and token/cost fields were null.

Run hosted-toolchain comparisons serially on storage-constrained Docker Desktop workstations. Do not raise concurrency above one without first provisioning several gigabytes of host-disk headroom and monitoring Docker writable-layer growth; infrastructure exhaustion invalidates an arm even when the task itself is healthy.

The next discriminating SYCL task must come from a real maintainer incident or upstream regression with non-obvious build/runtime evidence. The portfolio should not add target hardware or manufacture another link puzzle merely to make a skill appear useful.
