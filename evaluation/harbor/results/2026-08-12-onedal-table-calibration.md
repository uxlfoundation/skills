# Harbor skill comparison: `uxl-onedal`

Task: `onedal-table-orientation-regression`

## Outcome

- **NO QUALITY CHANGE: reward changed by +0.0000**
- Candidate versus no skill: +0.0000 reward.
- Candidate versus previous: +0.0000 reward, n/a cost.
- Quality gate at reward `1.0000`: candidate 1/1, previous 1/1.
- Efficiency: candidate tokens per verified success changed by +17.8%.
- Reliability: all runs completed without errors.
- Token accounting: recovered from raw Codex `turn.completed` events for No skill, Previous, Candidate because Harbor did not populate job-level usage.
- **Ceiling warning:** all three arms reached full reward; this task cannot distinguish skill value.

## Results

| Arm | Harbor job | Mean reward | Trials | Errors | Trial rewards | Uncached input | Cached input | Output | Cost | Runtime |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | [`onedal-table-native-calibration-20260812-noskill`](http://127.0.0.1:8080/jobs/onedal-table-native-calibration-20260812-noskill) | 1.0000 | 1/1 | 0 | 1.0000x1 | 11,496 | 62,208 | 1,072 | n/a | 2m 56s |
| Previous | [`onedal-table-native-calibration-20260812-previous`](http://127.0.0.1:8080/jobs/onedal-table-native-calibration-20260812-previous) | 1.0000 | 1/1 | 0 | 1.0000x1 | 15,523 | 77,312 | 1,413 | n/a | 3m 04s |
| Candidate | [`onedal-table-native-calibration-20260812-candidate`](http://127.0.0.1:8080/jobs/onedal-table-native-calibration-20260812-candidate) | 1.0000 | 1/1 | 0 | 1.0000x1 | 18,613 | 90,368 | 2,052 | n/a | 3m 13s |

## Verified-success efficiency

Quality gate: trial reward at least `1.0000`.

| Arm | Verified successes | Total token burn | Tokens / verified success | Cost / verified success |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 74,776 | 74,776 | n/a |
| Previous | 1/1 | 94,248 | 94,248 | n/a |
| Candidate | 1/1 | 111,033 | 111,033 | n/a |

## Metric breakdown

| Metric | No skill | Previous | Candidate | Candidate - previous |
| --- | ---: | ---: | ---: | ---: |
| `hidden_rectangular_rmse` | 0.0000 | 0.0000 | 0.0000 | +0.0000 |
| `hidden_wide_rmse` | 0.0000 | 0.0000 | 0.0000 | +0.0000 |
| `public_square_rmse` | 0.0000 | 0.0000 | 0.0000 | +0.0000 |
| `reward` | 1.0000 | 1.0000 | 1.0000 | +0.0000 |

## Provenance

- Task: `working-tree@186f8d7413ba42716f40ae386762468e93b5527f (content sha256 5bfa371a43cd2fa8c88447e6e367480368c911bf70c3e2911d7ad26340e9d68c; tree db190ec65aec05c9d42120770c80a96b8aaa8d6e)`
- Previous skill: `d9e3d28@d9e3d282bd31257219c3380f6570c2b42063cc95 (tree f45c7c5ff0d89a0671e6c3083400fe1e33b4bd53)`
- Candidate skill: `working-tree@186f8d7413ba42716f40ae386762468e93b5527f (content sha256 9f0deee9386d15cda93cb3ab941042da6ea172da84afca73c4201ddc2a3441a9; tree a7d2e5f09eb81fcb7e7f224616ec5bac0a755a0c)`
- Agent/model: `codex` / `gpt-5.6-sol`
- Attempts per arm: `1`
- Verified reward floor: `1.0000`
- No-skill result: `harbor-jobs/onedal-table-native-calibration-20260812-noskill/result.json`
- Previous result: `harbor-jobs/onedal-table-native-calibration-20260812-previous/result.json`
- Candidate result: `harbor-jobs/onedal-table-native-calibration-20260812-candidate/result.json`

Review any changed or failed trial in Harbor: inspect **Verifier** for the score, **Artifacts** for the submitted answer/code, and **Trajectory** for the exact composed prompt and agent behavior.
