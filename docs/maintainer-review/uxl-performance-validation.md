# Cross-project performance-validation skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-performance-validation` for technical accuracy, conservative claim discipline, useful cross-project scope, and suitability for shared UXL ownership.

The skill covers correctness gates, baseline and timing-scope selection, warmup and variance, synchronization, tolerances, resource constraints, benchmark reporting, and conservative performance claims.

Why this helps: agents must show a valid comparison and bounded evidence before turning a local measurement into a project or hardware claim.

The initial ask is a 45-minute review of the benchmark contract and ownership model—not a commitment to standardize every project's benchmarks.

## Evidence to inspect

- Instructions: `skills/uxl-performance-validation/SKILL.md`
- Benchmark contract: `skills/uxl-performance-validation/references/benchmark-contract.md`
- Official sources: `skills/uxl-performance-validation/references/official-sources.md`
- Prompt evals: `skills/uxl-performance-validation/evals/evals.json`
- Public card: `skill-cards/uxl-performance-validation.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-performance-validation`)

Coverage state: 4 of 6 declared tasks implemented; no current task retains measured skill headroom, so the suite does not yet prove quality lift. One executable task is sourced from a oneTBB maintainer incident. Planned tasks need transfer-inclusive and profiler-after-regression evidence on declared target lanes. Official sources were rechecked on 2026-09-04.

## Suggested reviewers

Please route through the UXL Open Source Working Group and include project benchmark owners plus representatives for the target platforms used in any claim. No individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Correctness, timing, warmup, variance, and tolerance rules are sound.
- [ ] Claims remain bounded to measured software and hardware configurations.
- [ ] The shared guidance does not override project-specific benchmark policy.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A working-group team will own or periodically review the shared skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
