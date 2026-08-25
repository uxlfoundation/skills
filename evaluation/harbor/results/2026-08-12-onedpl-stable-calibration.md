# Harbor skill comparison: `uxl-onedpl`

Task: `onedpl-stable-ordering-contract`

## Outcome

- **NO QUALITY CHANGE: reward changed by +0.0000**
- Candidate versus no skill: +0.0000 reward.
- Candidate versus previous: +0.0000 reward, +22.9% cost.
- Quality gate at reward `1.0000`: candidate 1/1, previous 1/1.
- Efficiency: candidate tokens per verified success changed by +9.9%; candidate cost per verified success changed by +22.9%.
- Reliability: all runs completed without errors.
- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value.

This one-attempt screen is not a statistical estimate. It is sufficient to classify the task as a ceiling/smoke check and provides no evidence for retaining the added task-specific skill wording, which was removed. The broader oneDPL skill remains subject to calibration on harder tasks with genuine headroom.

## Results

| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | [`onedpl-stable-calibration-20260812-noskill`](http://127.0.0.1:8080/jobs/onedpl-stable-calibration-20260812-noskill) | 1.0000 | 1/1 | 0 | 1.0000x1 | 13,878 | 77,312 | 1,463 | $0.151936 | 4m 29s |
| Previous | [`onedpl-stable-calibration-20260812-previous`](http://127.0.0.1:8080/jobs/onedpl-stable-calibration-20260812-previous) | 1.0000 | 1/1 | 0 | 1.0000x1 | 21,988 | 141,056 | 2,460 | $0.254268 | 4m 28s |
| Candidate | [`onedpl-stable-calibration-20260812-candidate`](http://127.0.0.1:8080/jobs/onedpl-stable-calibration-20260812-candidate) | 1.0000 | 1/1 | 0 | 1.0000x1 | 34,745 | 144,896 | 2,207 | $0.312383 | 5m 08s |

## Verified-success efficiency

Quality gate: trial reward at least `1.0000`.

| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 92,653 | 92,653 | $0.151936 |
| Previous | 1/1 | 165,504 | 165,504 | $0.254268 |
| Candidate | 1/1 | 181,848 | 181,848 | $0.312383 |

## Metric breakdown

| Metric | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| `reward` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |
| `stable_cases` | 4.0000 | 4.0000 | 4.0000 | +0.0000 |

## Provenance

- Task: `working-tree@702200f394426b407d240627f3c9467ffeeb925c (content sha256 8d5888b510d5fb135e63ab15f7edc64377df3a3940eb761611431ae652b30e99; tree 307a95a9031a9b002b44b3f8be4bfc91ab0cfc5f)`
- Previous skill: `5540f22@5540f2206bc557b087a892fa0fbf7ccd6933492e (tree 5d98ba2db5071a9e1cf81133b2f4789ae5a33efd)`
- Candidate skill: `working-tree@702200f394426b407d240627f3c9467ffeeb925c (content sha256 8501e077581829ce7196e86fc23ffec2b53faff30de58ab3b6d15f3b8a0f685c; tree b9887292a40c9af9928bcb15eb4323076e131594)`
- Agent/model: `codex` / `gpt-5.6-sol`
- Attempts per arm: `1`
- Verified reward floor: `1.0000`
- No-skill result: `harbor-jobs/onedpl-stable-calibration-20260812-noskill/result.json`
- Previous result: `harbor-jobs/onedpl-stable-calibration-20260812-previous/result.json`
- Candidate result: `harbor-jobs/onedpl-stable-calibration-20260812-candidate/result.json`

Review any changed or failed trial in Harbor: inspect **Verifier** for the score, **Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.
