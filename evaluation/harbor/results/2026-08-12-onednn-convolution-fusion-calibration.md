# Harbor skill comparison: `uxl-onednn`

Task: `onednn-convolution-fusion-parity`

## Outcome

- **NO QUALITY CHANGE: reward changed by +0.0000**
- Candidate versus no skill: +0.0000 reward.
- Candidate versus previous: +0.0000 reward, -3.0% cost.
- Quality gate at reward `1.0000`: candidate 1/1, previous 1/1.
- Efficiency: candidate tokens per verified success changed by -21.5%; candidate cost per verified success changed by -3.0%.
- Reliability: all runs completed without errors.
- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value.

This one-attempt screen is not a statistical estimate. It is sufficient to classify the task as a ceiling/smoke check. The candidate used 21.5% fewer tokens than the original skill but 6.5% more than no skill, with no quality difference; therefore this task provides no evidence that the skill improves token efficiency. The preceding [invalid calibration](2026-08-12-onednn-convolution-fusion-calibration-invalid.md) is excluded because the original verifier rejected implementation-equivalent repairs before writing reward files.

## Results

| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | [`onednn-fusion-valid-calibration-20260812-noskill`](http://127.0.0.1:8080/jobs/onednn-fusion-valid-calibration-20260812-noskill) | 1.0000 | 1/1 | 0 | 1.0000x1 | 22,845 | 90,368 | 2,061 | $0.221239 | 3m 45s |
| Previous | [`onednn-fusion-valid-calibration-20260812-previous`](http://127.0.0.1:8080/jobs/onednn-fusion-valid-calibration-20260812-previous) | 1.0000 | 1/1 | 0 | 1.0000x1 | 18,886 | 134,912 | 2,704 | $0.243006 | 4m 30s |
| Candidate | [`onednn-fusion-valid-calibration-20260812-candidate`](http://127.0.0.1:8080/jobs/onednn-fusion-valid-calibration-20260812-candidate) | 1.0000 | 1/1 | 0 | 1.0000x1 | 21,634 | 98,560 | 2,605 | $0.235600 | 5m 02s |

## Verified-success efficiency

Quality gate: trial reward at least `1.0000`.

| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 115,274 | 115,274 | $0.221239 |
| Previous | 1/1 | 156,502 | 156,502 | $0.243006 |
| Candidate | 1/1 | 122,799 | 122,799 | $0.235600 |

## Metric breakdown

| Metric | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| `hidden_cases` | 4.0000 | 4.0000 | 4.0000 | +0.0000 |
| `max_abs_error` | 0.0000 | 0.0000 | 0.0000 | +0.0000 |
| `reward` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |

## Provenance

- Task: `working-tree@450b47ad1b610fb9b68ecdfd9ecc2caa833750f3 (content sha256 8bf12c09d38ffdbd0f86313242ebe6a0038cedf03f189e0adc194e2b10b95b57; tree dbf06e17d763a04e6d0f50fd994db78d61192b26)`
- Previous skill: `476bfc8@476bfc8ec2acee684ef2452484cba9912142a725 (tree a684e8961181d57958b535802b82723d5fd57aa8)`
- Candidate skill: `working-tree@450b47ad1b610fb9b68ecdfd9ecc2caa833750f3 (content sha256 e3c529efa6b0ff12f8686d22ab05574c8ba434cbc561a9dd72f9fee2fbb2f2f6; tree 95f15d06e24273d18a6d918b4c5128fff10f7828)`
- Agent/model: `codex` / `gpt-5.6-sol`
- Attempts per arm: `1`
- Verified reward floor: `1.0000`
- No-skill result: `harbor-jobs/onednn-fusion-valid-calibration-20260812-noskill/result.json`
- Previous result: `harbor-jobs/onednn-fusion-valid-calibration-20260812-previous/result.json`
- Candidate result: `harbor-jobs/onednn-fusion-valid-calibration-20260812-candidate/result.json`

Review any changed or failed trial in Harbor: inspect **Verifier** for the score, **Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.
