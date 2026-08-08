# Coverage wave 1: 2026-08-08

This wave added first-task coverage for oneCCL, oneDAL, oneDNN, oneDPL, performance validation, and SYCL build/debug. The same Codex agent was sampled with and without the relevant skill. Rubrics were then audited against the answer artifacts to remove false negatives caused by overly literal wording checks.

## Directional one-attempt results

These rewards are post-hoc scores from the current audited rubrics. They are useful for selecting calibration candidates, but they are not promotion evidence.

| Skill | Task | Baseline | Skill | Difference | Classification |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-oneccl` | `oneccl-divergent-collective-sequence` | 0.4444 | 1.0000 | +0.5556 | Directional headroom |
| `uxl-onedal` | `onedal-sklearn-or-native-kmeans` | 0.6667 | 1.0000 | +0.3333 | Directional headroom |
| `uxl-onednn` | `onednn-framework-blocked-layout` | 0.5556 | 1.0000 | +0.4444 | Advanced to calibration |
| `uxl-onedpl` | `onedpl-missing-device-synchronization` | 0.6667 | 1.0000 | +0.3333 | Directional headroom |
| `uxl-sycl-build-debug` | `sycl-cmake-compiler-cache` | 0.4444 | 0.8889 | +0.4445 | Directional headroom |
| `uxl-performance-validation` | `performance-tiny-async-gpu-claim` | 0.8889 | 0.8889 | 0.0000 | Smoke/near-ceiling |

The performance task was reclassified from discriminating to smoke because both arms were near ceiling and the sampled skill produced no lift. The other four directional tasks remain `uncalibrated` until they receive the manifest's required three attempts per arm.

## oneDNN three-attempt calibration

The two additional attempts per arm used the unchanged oneDNN task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.5556, 0.7778, 0.7778 | 0.7037 | 110,219 | 92,160 | 2,882 | $0.222835 |
| `uxl-onednn` | 1.0000, 0.8889, 1.0000 | 0.9630 | 246,905 | 218,880 | 5,485 | $0.414115 |
| Difference |  | +0.2593 |  |  |  |  |

All six valid oneDNN trials completed without errors. This confirms measurable headroom for `onednn-framework-blocked-layout`, so its calibration state is `headroom`.

## Reliability note

The first six-task baseline job experienced a temporary network/DNS outage while reaching the Codex service. Three trials ended with `NonZeroAgentExitCodeError`; they were excluded rather than scored as task failures. The same oneDNN, oneDPL, and performance tasks were retried unchanged after connectivity recovered, and all completed normally.

## Reproduction and provenance

- Harbor: `0.20.0`
- Agent: `codex`
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Codex CLI in trial images: `0.144.4`
- Calibration attempts per arm: `3`
- Concurrency: `1`
- Task, instruction, and skill starting revision: `b5eda8c`
- Rubric revision: this report's repository revision

Jobs used for the oneDNN calibration:

- Initial baseline probe: `coverage-wave1-baseline-gpt56-probe-r2`
- Initial skill probe: `coverage-wave1-onednn-skill-gpt56-probe`
- Additional baseline attempts: `coverage-wave1-onednn-baseline-gpt56-calibration-r2`
- Additional skill attempts: `coverage-wave1-onednn-skill-gpt56-calibration-r2`

The other skill-arm jobs use the corresponding `coverage-wave1-<skill>-skill-gpt56-probe` names. The initial valid baseline results for oneCCL, oneDAL, and SYCL came from `coverage-wave1-baseline-gpt56-probe`; the retry job above supplied oneDNN, oneDPL, and performance. Raw Harbor jobs remain in the ignored local `harbor-jobs` directory and can be inspected with:

```powershell
harbor view harbor-jobs
```
