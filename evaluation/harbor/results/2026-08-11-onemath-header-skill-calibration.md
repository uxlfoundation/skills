# oneMath compatibility-header skill calibration: 2026-08-11

This calibration measures whether the `uxl-onemath` skill improves a real but intentionally easy installed-header incident. The task is useful as deterministic regression coverage, but all three treatments reached full reward. It therefore cannot demonstrate a quality improvement from the skill.

## Reproducibility repair

The first planned nine-trial run was invalid: all trials failed before agent startup because the task downloaded its pinned oneMath archive from GitHub during the Docker build and the WSL builder could not reach GitHub. Those jobs reported zero tokens and are excluded from calibration.

Commit `b9ac03a` made the task self-contained by vendoring the two exact affected upstream headers and stubbing unrelated domain headers. An uncached WSL build then passed, with reward 0 before repair and reward 1 after repair. A one-attempt-per-arm model probe also passed before the full calibration was repeated.

## Three-attempt calibration

Each arm used three serial attempts with the same committed task, model, reasoning effort, timeout, and treatment instruction. All nine trials completed without exceptions.

| Arm | Mean reward | Verified successes | Uncached input | Cached input | Output | Total token burn | Tokens / success | Cost | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No skill | 1.0000 | 3/3 | 43,017 | 219,648 | 2,637 | 265,302 | 88,434 | $0.404019 | 5m 36s |
| Previous skill | 1.0000 | 3/3 | 74,402 | 433,408 | 6,253 | 514,063 | 171,354 | $0.776304 | 6m 45s |
| Candidate skill | 1.0000 | 3/3 | 53,637 | 423,680 | 6,229 | 483,546 | 161,182 | $0.666895 | 5m 48s |

| Arm | Trial 1 total tokens | Trial 2 total tokens | Trial 3 total tokens |
| --- | ---: | ---: | ---: |
| No skill | 98,263 | 83,398 | 83,641 |
| Previous skill | 200,407 | 128,987 | 184,669 |
| Candidate skill | 189,542 | 146,506 | 147,498 |

## Artifact audit

All nine trajectories reproduced the failure, found `oneapi/mkl/namespace_alias.hpp`, changed the compatibility header, reran the reproducer, and received reward 1. The verifier independently required the corrected installed-tree include, every preserved oneMath domain include, the processed namespace-alias header, and the deprecated `oneapi::mkl` alias.

Skill-enabled agents read the skill and supporting references and generally performed more inspection than no-skill agents. The task itself contains enough local evidence for the model to solve it reliably without project guidance.

## Interpretation and decision

The candidate used 5.9% fewer total tokens and 14.1% less cost than the previous skill, but it used 82.3% more tokens and 65.1% more cost than no skill while producing identical quality. With only three trials and substantial per-trial variance, the candidate-versus-previous improvement is directional rather than conclusive.

Classify `onemath-deprecated-header-include` as `ceiling` and retain it as smoke/regression coverage. Do not use it as evidence that the oneMath skill improves quality or token efficiency. Future skill claims should preserve verified success while reducing tokens per verified success across harder tasks where project guidance changes agent behavior. This follows [official OpenAI guidance](https://developers.openai.com/api/docs/guides/latest-model) to compare representative-task success, evidence, tokens, latency, and cost, and to count resource reductions only when the quality bar still passes.

## Provenance

- Agent/model: `codex` / `gpt-5.6-sol`.
- Reasoning effort: `medium`.
- Attempts per arm: 3; concurrency: 1.
- Task revision: `b9ac03a`.
- Previous skill: `91722c5`.
- Candidate skill tree: `3025e68b02d7468781baa9d9baf3cbaf600e69ac`.
- Job prefix: `onemath-header-calibration-offline-20260811`.

Dashboard jobs:

- [No skill](http://127.0.0.1:8080/jobs/onemath-header-calibration-offline-20260811-noskill)
- [Previous skill](http://127.0.0.1:8080/jobs/onemath-header-calibration-offline-20260811-previous)
- [Candidate skill](http://127.0.0.1:8080/jobs/onemath-header-calibration-offline-20260811-candidate)
