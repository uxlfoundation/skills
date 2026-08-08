# Coverage wave 1: 2026-08-08

This wave added first-task coverage for oneCCL, oneDAL, oneDNN, oneDPL, performance validation, and SYCL build/debug. The same Codex agent was sampled with and without the relevant skill. Rubrics were then audited against the answer artifacts to remove false negatives caused by overly literal wording checks.

## Directional one-attempt results

These rewards are post-hoc scores from the current audited rubrics. They are useful for selecting calibration candidates, but they are not promotion evidence.

| Skill | Task | Baseline | Skill | Difference | Classification |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-oneccl` | `oneccl-divergent-collective-sequence` | 0.4444 | 1.0000 | +0.5556 | Advanced to calibration |
| `uxl-onedal` | `onedal-sklearn-or-native-kmeans` | 0.6667 | 1.0000 | +0.3333 | Advanced to calibration |
| `uxl-onednn` | `onednn-framework-blocked-layout` | 0.5556 | 1.0000 | +0.4444 | Advanced to calibration |
| `uxl-onedpl` | `onedpl-missing-device-synchronization` | 0.6667 | 1.0000 | +0.3333 | Advanced to calibration |
| `uxl-sycl-build-debug` | `sycl-cmake-compiler-cache` | 0.4444 | 0.8889 | +0.4445 | Advanced to calibration |
| `uxl-performance-validation` | `performance-tiny-async-gpu-claim` | 0.8889 | 0.8889 | 0.0000 | Smoke/near-ceiling |

The performance task was reclassified from discriminating to smoke because both arms were near ceiling and the sampled skill produced no lift. All five discriminating tasks from this wave advanced to the manifest's required three attempts per arm and retained positive mean skill lift.

## Calibrated summary

| Skill | Task | Baseline mean | Skill mean | Difference | State |
| --- | --- | ---: | ---: | ---: | --- |
| `uxl-onednn` | `onednn-framework-blocked-layout` | 0.7037 | 0.9630 | +0.2593 | Headroom |
| `uxl-oneccl` | `oneccl-divergent-collective-sequence` | 0.4074 | 0.6667 | +0.2593 | Headroom |
| `uxl-sycl-build-debug` | `sycl-cmake-compiler-cache` | 0.4444 | 0.5926 | +0.1482 | Headroom, variable |
| `uxl-onedal` | `onedal-sklearn-or-native-kmeans` | 0.6297 | 0.8889 | +0.2592 | Headroom |
| `uxl-onedpl` | `onedpl-missing-device-synchronization` | 0.5926 | 0.8519 | +0.2593 | Headroom |

## oneDNN three-attempt calibration

The two additional attempts per arm used the unchanged oneDNN task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.5556, 0.7778, 0.7778 | 0.7037 | 110,219 | 92,160 | 2,882 | $0.222835 |
| `uxl-onednn` | 1.0000, 0.8889, 1.0000 | 0.9630 | 246,905 | 218,880 | 5,485 | $0.414115 |
| Difference |  | +0.2593 |  |  |  |  |

All six valid oneDNN trials completed without errors. This confirms measurable headroom for `onednn-framework-blocked-layout`, so its calibration state is `headroom`.

## oneCCL three-attempt calibration

The two additional attempts per arm used the unchanged oneCCL task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.4444, 0.3333, 0.4444 | 0.4074 | 165,520 | 132,096 | 3,882 | $0.349628 |
| `uxl-oneccl` | 1.0000, 0.4444, 0.5556 | 0.6667 | 246,692 | 202,496 | 5,226 | $0.479008 |
| Difference |  | +0.2593 |  |  |  |  |

All six valid oneCCL trials completed without errors. This confirms measurable headroom for `oneccl-divergent-collective-sequence`, so its calibration state is `headroom`. The skill arm improved diagnosis and evidence collection, although validation remained the weakest rubric group in the two additional samples; future oneCCL tasks should therefore test executable collective contracts as well as answer quality.

## SYCL three-attempt calibration

The two additional attempts per arm used the unchanged SYCL task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.4444, 0.6667, 0.2222 | 0.4444 | 168,302 | 114,176 | 6,381 | $0.519148 |
| `uxl-sycl-build-debug` | 0.8889, 0.5556, 0.3333 | 0.5926 | 260,535 | 219,904 | 9,103 | $0.586197 |
| Difference |  | +0.1482 |  |  |  |  |

All six valid SYCL trials completed without errors. The repeated samples show more variance than the first pair, but the three-attempt skill mean remains higher, so `sycl-cmake-compiler-cache` is marked `headroom`. Its next companion task should emphasize clean reconfiguration and runtime-device proof, the least consistent validation behaviors in this sample.

## oneDAL three-attempt calibration

The two additional attempts per arm used the unchanged oneDAL task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.6667, 0.5556, 0.6667 | 0.6297 | 154,098 | 127,232 | 4,554 | $0.334566 |
| `uxl-onedal` | 1.0000, 0.7778, 0.8889 | 0.8889 | 337,394 | 271,872 | 6,913 | $0.670936 |
| Difference |  | +0.2592 |  |  |  |  |

All six valid oneDAL trials completed without errors. This confirms measurable headroom for `onedal-sklearn-or-native-kmeans`, so its calibration state is `headroom`.

## oneDPL three-attempt calibration

The two additional valid attempts per arm used the unchanged oneDPL task, skill, and audited rubric. The first attempt in each arm is the earlier probe re-scored with that same rubric.

| Arm | Trial rewards | Mean reward | Input tokens | Cache-read tokens | Output tokens | Cost (USD) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No skill | 0.6667, 0.4444, 0.6667 | 0.5926 | 336,716 | 278,272 | 6,148 | $0.615796 |
| `uxl-onedpl` | 1.0000, 0.7778, 0.7778 | 0.8519 | 727,715 | 602,368 | 9,071 | $1.200049 |
| Difference |  | +0.2593 |  |  |  |  |

All six scored oneDPL trials completed without errors. This confirms measurable headroom for `onedpl-missing-device-synchronization`, so its calibration state is `headroom`.

## Reliability note

The first six-task baseline job experienced a temporary network/DNS outage while reaching the Codex service. Three trials ended with `NonZeroAgentExitCodeError`; they were excluded rather than scored as task failures. The same oneDNN, oneDPL, and performance tasks were retried unchanged after connectivity recovered, and all completed normally.

A later oneDPL calibration attempt hit the same DNS failure in all four trials before any answer was written. Those trials in the `r2` jobs were also excluded. A container-level DNS and HTTPS probe then passed, and the unchanged `r3` baseline and skill jobs completed 2/2 without errors.

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

Jobs used for the oneCCL calibration:

- Initial baseline probe: `coverage-wave1-baseline-gpt56-probe`
- Initial skill probe: `coverage-wave1-oneccl-skill-gpt56-probe`
- Additional baseline attempts: `coverage-wave1-oneccl-baseline-gpt56-calibration-r2`
- Additional skill attempts: `coverage-wave1-oneccl-skill-gpt56-calibration-r2`

Jobs used for the SYCL calibration:

- Initial baseline probe: `coverage-wave1-baseline-gpt56-probe`
- Initial skill probe: `coverage-wave1-sycl-skill-gpt56-probe`
- Additional baseline attempts: `coverage-wave1-sycl-baseline-gpt56-calibration-r2`
- Additional skill attempts: `coverage-wave1-sycl-skill-gpt56-calibration-r2`

Jobs used for the oneDAL calibration:

- Initial baseline probe: `coverage-wave1-baseline-gpt56-probe`
- Initial skill probe: `coverage-wave1-onedal-skill-gpt56-probe`
- Additional baseline attempts: `coverage-wave1-onedal-baseline-gpt56-calibration-r2`
- Additional skill attempts: `coverage-wave1-onedal-skill-gpt56-calibration-r2`

Jobs used for the oneDPL calibration:

- Initial baseline probe: `coverage-wave1-baseline-gpt56-probe-r2`
- Initial skill probe: `coverage-wave1-onedpl-skill-gpt56-probe`
- Excluded outage attempts: `coverage-wave1-onedpl-baseline-gpt56-calibration-r2`, `coverage-wave1-onedpl-skill-gpt56-calibration-r2`
- Valid additional baseline attempts: `coverage-wave1-onedpl-baseline-gpt56-calibration-r3`
- Valid additional skill attempts: `coverage-wave1-onedpl-skill-gpt56-calibration-r3`

The other skill-arm jobs use the corresponding `coverage-wave1-<skill>-skill-gpt56-probe` names. The initial valid baseline results for oneCCL, oneDAL, and SYCL came from `coverage-wave1-baseline-gpt56-probe`; the retry job above supplied oneDNN, oneDPL, and performance. Raw Harbor jobs remain in the ignored local `harbor-jobs` directory and can be inspected with:

```powershell
harbor view harbor-jobs
```
