# oneDNN benchdnn incident calibration: 2026-08-13

## Outcome

The current `uxl-onednn` skill preserved verified success on the live oneDNN `benchdnn` maintainer incident while reducing the portfolio's primary efficiency metric. All nine matched trials passed with reward `1.0` and no exceptions. The current skill used **485,077 tokens per verified success**, 11.6% fewer than no skill and 68.1% fewer than the original catalog skill.

This remains a quality-ceiling smoke task: every arm repaired and verified the incident, so it does not show a quality lift. It does provide three-attempt evidence that the current concise skill can reduce investigation cost on a real project workflow without lowering quality. Promotion evidence still requires five attempts per arm under the portfolio policy.

## Matched results

| Arm | Verified successes | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 3/3 | 548,989 | $0.610954 | 12m 44s |
| Original skill (`476bfc8`) | 3/3 | 1,520,897 | $1.378821 | 16m 42s |
| Current skill (`643bc0f`) | 3/3 | 485,077 | $0.564786 | 11m 00s |

Candidate changes:

- Versus no skill: 11.6% fewer tokens per verified success, 7.6% lower cost per verified success, and 13.7% lower runtime.
- Versus the original skill: 68.1% fewer tokens per verified success, 59.0% lower cost per verified success, and 34.1% lower runtime.

The one-attempt development screen pointed in the same direction: all arms passed, while the current skill used 448,569 tokens, versus 876,923 without a skill and 1,716,185 with the original skill. The three-attempt result above is the calibration evidence.

## Infrastructure audit

The first cold oracle attempt is excluded because the pinned historical oneDNN image exceeded the original 30-minute environment-start allowance while still compiling. A 60-minute cold-build allowance now reflects the observed two-CPU build. The cached oracle retry passed at reward `1.0` with no exception.

The first model comparison is also excluded because the intentionally crashing pre-fix `benchdnn` process caused WSL 2.6.3 to retain large host crash dumps until C: filled and Docker stopped. The Windows comparison wrapper now offers an opt-in `-GuardWslCrashDumps` switch. During the valid calibration it kept newly generated WSL dump bytes at zero while preserving the process exit status, task output, Harbor artifacts, and verifier behavior. All nine valid trials completed without infrastructure errors.

## Classification and next gate

Classify `onednn-benchdnn-no-ref-memory` as `ceiling`: it is durable real-incident regression coverage and positive token-efficiency evidence, but not quality-discriminating evidence. Retain the current skill wording because it reduced token burn across three matched attempts without sacrificing verified success.

Do not spend five-attempt promotion budget on this task alone. First implement or calibrate another harder oneDNN task with quality headroom or an independently phrased real triage workflow. If the efficiency benefit generalizes across that suite, run five matched attempts per arm for promotion evidence.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 3; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `643bc0fa1b02d28153419f67687db17a6bbd36be`.
- Valid job prefix: `onednn-benchdnn-calibration-20260813-r3`.
- Raw comparison: `harbor-jobs/onednn-benchdnn-calibration-20260813-r3-comparison.md`.
- Oracle retry: `harbor-jobs/onednn-benchdnn-oracle-20260812-r3/result.json`.
