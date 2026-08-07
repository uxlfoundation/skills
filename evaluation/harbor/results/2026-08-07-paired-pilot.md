# Paired Harbor pilot: 2026-08-07

This exploratory pilot compares the same Codex agent with and without the relevant UXL skill. Each arm used three serial attempts against the same task revision. All 12 trials completed without exceptions.

## Results

| Project | Task | Arm | Mean reward | Input tokens | Output tokens | Cost (USD) | Runtime |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| oneMath | `onemath-runtime-library-missing` | Baseline | 0.9111 | 162,415 | 2,839 | $0.279773 | 230.7 s |
| oneMath | `onemath-runtime-library-missing` | Skill | 1.0000 | 353,864 | 5,676 | $0.683920 | 250.6 s |
| oneTBB | `onetbb-histogram-local-aggregation` | Baseline | 1.0000 | 347,909 | 7,645 | $0.627967 | 347.0 s |
| oneTBB | `onetbb-histogram-local-aggregation` | Skill | 1.0000 | 541,079 | 12,125 | $0.946009 | 476.3 s |

The oneMath skill improved mean reward by **0.0889**. Its `required_terms` component increased from 0.7333 to 1.0000 while `answer_present` and `unsupported_claim_avoidance` remained at 1.0000. The skill answers consistently added domain-specific backend flags and wrapper libraries, explicit SYCL queue/device evidence, support-matrix validation, loader checks, and separate correctness and performance validation. This gain used 117.9% more input tokens, 99.9% more output tokens, and 144.5% more cost.

The oneTBB score delta was **0.0000**. Every baseline and skill attempt passed, and all six artifacts independently implemented essentially the same `oneapi::tbb::parallel_reduce` with partition-local histograms. This task is useful as a regression check, but it is too easy for this agent/model combination to measure incremental skill value. A follow-up oneTBB task should require more architectural judgment or expose multiple plausible-but-wrong concurrency strategies.

These are pilot signals, not promotion evidence: the sample is small, each project has one task, and no attempt was made to estimate variance across prompts, models, or task revisions.

## Reproduction and provenance

- Harbor: `0.20.0`
- Agent: `codex`
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Codex CLI in trial images: `0.144.4`
- Attempts per arm: `3`
- Concurrency: `1`
- Repository revision: `707bb1f2d1eb1827c6e74c064b4cc0352998a85f`
- oneMath task tree: `8c4780722d228c5b9a127688683d2ab4901668fe`
- `uxl-onemath` skill tree: `fc734c64fae3439816b93a286fd7c2921a9b90f5`
- oneTBB task tree: `47872391bf3bf792e7f26b0f32421a831bed238e`
- `uxl-onetbb` skill tree: `f506af760d6cec12a5febfc8ddb0ec8156d12d62`

Job names:

- `onemath-baseline-gpt56-20260807-r3`
- `onemath-skill-gpt56-20260807-r1`
- `onetbb-baseline-gpt56-20260807-r1`
- `onetbb-skill-gpt56-20260807-r1`

Raw Harbor jobs remain in the ignored local `harbor-jobs` directory. From the repository root, run:

```powershell
harbor view harbor-jobs
```

The local Python and Ubuntu base images were preloaded with the same Codex CLI and agent prerequisites Harbor otherwise installs at trial startup. Task instructions, environments, solutions, and verifiers were not changed between paired arms.
