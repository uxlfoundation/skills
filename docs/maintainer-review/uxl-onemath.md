# oneMath skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-onemath` for technical accuracy, useful scope, honest limitations, and suitability as a oneMath-maintained coding-agent skill.

The skill covers domain and usage-model selection, runtime versus compile-time dispatch, backend selectors, SYCL queue ownership, build/link diagnosis, and the steps needed to integrate a third-party backend.

Why this helps: agents are steered toward oneMath's actual dispatch and integration model and away from confusing oneMath with oneMKL or inventing backend support.

The initial ask is a 30–45 minute accuracy and source-refresh review plus a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-onemath/SKILL.md`
- Official sources: `skills/uxl-onemath/references/official-sources.md`
- Detailed references: `skills/uxl-onemath/references/`
- Prompt evals: `skills/uxl-onemath/evals/evals.json`
- Public card: `skill-cards/uxl-onemath.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-onemath`)

Coverage state: 3 of 6 declared tasks implemented; 1 task retains measured headroom; 2 implemented tasks are sourced from maintainer incidents. Planned coverage includes RNG event chaining, third-party backend integration, and dispatch-overhead measurement. Sources were last checked on 2026-06-26 and need a current release check before promotion.

## Suggested reviewers

Please route to current oneMath maintainers responsible for public APIs, build systems, backend integration, and device/runtime support. No individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Dispatch, queue, build/link, and backend-integration guidance is correct.
- [ ] Backend and compiler limitations are stated neutrally and currently.
- [ ] Source ledger is refreshed and sufficient.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
