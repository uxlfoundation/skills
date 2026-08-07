# 2026-08-07 evaluator expansion

This iteration added a harder executable oneTBB task and replaced the oneMath pilot's keyword counter with a structured diagnostic rubric.

## oneMath rubric calibration

The new verifier was applied offline to the answer artifacts from the recorded three-attempt pilot. This is a post-hoc rubric calibration, not a new Harbor model run; the original job rewards remain immutable in their job directories.

| Arm | Re-scored trial rewards | Mean |
| --- | --- | ---: |
| No skill | 0.3333, 0.5556, 0.5556 | 0.4815 |
| `uxl-onemath` | 1.0000, 0.7778, 0.6667 | 0.8148 |
| Difference |  | +0.3333 |

The rubric now scores three diagnosis criteria, three evidence-collection criteria, and three staged-validation criteria. It also requires a substantive answer and rejects direct unsupported claims. Unit tests establish that the oracle answer scores 1.0 while the old five-keyword strategy scores 0.

## oneTBB stable-compaction probe

The new `onetbb-stable-compaction-scan` task verifies stable ordering under one, two, and four worker limits, repeated scheduling, edge cases, and a seeded 250,000-element input. The starter's atomic writes are race-free at each slot but nondeterministically assign those slots, so the starter earns 0. The oracle solution earns 1.0.

A matched one-attempt probe with `gpt-5.6-sol` at medium reasoning produced:

| Arm | Passing trials | Mean reward |
| --- | ---: | ---: |
| No skill | 1/1 | 1.0000 |
| `uxl-onetbb` | 1/1 | 1.0000 |

This is executable regression coverage, not evidence of oneTBB skill lift: the sampled model already selected the correct prefix-scan pattern without the skill. A three-attempt no-skill run of an earlier, more explicit prompt also scored 3/3 and was excluded from the matched table after the prompt was tightened.

## Validation and interpretation

- Harbor oracle: all three hosted tasks passed at reward 1.0.
- oneMath is the current discriminating pilot for baseline-versus-skill comparisons.
- The oneTBB histogram remains a smoke task, while stable compaction adds stronger deterministic and ordering coverage.
- Future oneTBB discrimination work should target integration decisions such as nested runtimes, arena limits, cancellation, or scheduler-sensitive performance rather than basic pattern recall alone.
