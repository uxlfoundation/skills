# oneTBB join-node calibration: 2026-08-13

## Outcome

The maintainer-sourced `onetbb-join-node-ordering` task is a quality ceiling under the current model. The no-skill, original-skill, and current-skill arms all repaired and verified the ordering failure at reward `1.0` with no exceptions.

The task remains valuable as live, hosted-CPU regression coverage for a real oneTBB incident, but it cannot demonstrate skill quality. It is reclassified from `discriminating` to `smoke`, and no three-attempt quality calibration is warranted.

## Matched results

| Arm | Verified successes | Tokens / verified success | Cost / verified success | Runtime |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/1 | 181,963 | $0.282888 | 3m 43s |
| Original skill (`476bfc8`) | 1/1 | 284,046 | $0.529893 | 4m 21s |
| Current skill (`5da329c`) | 1/1 | 292,895 | $0.464853 | 4m 19s |

Candidate changes:

- Versus no skill: 61.0% more tokens per verified success, 64.3% higher cost, and 16.1% longer runtime.
- Versus the original skill: 3.1% more tokens per verified success, 12.3% lower cost, and 0.8% shorter runtime.

This one-attempt screen is sufficient to identify a full-quality ceiling, but not to estimate efficiency statistically. It provides no evidence that the current skill reduces token burn on this task.

## Repair audit

The verifier accepts either graph-level repair requested by the task and checks behavior under four-way concurrency across repeated and boundary-size runs:

- the no-skill arm inserted a `sequencer_node` keyed by the source token before the second queueing join;
- both skill arms replaced the second queueing join with a `key_matching` join keyed by token value.

All three solutions preserve the public interface, keep the oneTBB flow graph, avoid a global one-thread limit, emit every source exactly once, and pair it with the matching counterpart. The different valid implementations confirm that the verifier is not tied to the oracle's spelling.

## Classification and next gate

Classify the task as `ceiling` and retain it as smoke/regression coverage. With this result, all 28 implemented tasks have a calibration state. Future oneTBB skill evidence should come from the two existing headroom tasks or a harder independently sourced incident—not more repetitions of this ceiling case.

## Reproduction

- Agent/model: `codex` / `gpt-5.6-sol`; reasoning effort `medium`.
- Attempts per arm: 1; concurrency: 1.
- Previous skill: `476bfc8ec2acee684ef2452484cba9912142a725`.
- Task and current skill revision: `5da329c812174dc98f9f17af14a827c7a64e452f`.
- Oracle job: `harbor-jobs/onetbb-join-ordering-oracle-20260813/result.json`.
- Comparison prefix: `onetbb-join-calibration-20260813`.
- Raw comparison: `harbor-jobs/onetbb-join-calibration-20260813-comparison.md`.
