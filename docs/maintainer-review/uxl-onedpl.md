# oneDPL skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-onedpl` for technical accuracy, useful scope, honest limitations, and suitability as a oneDPL-maintained coding-agent skill.

The skill covers execution-policy choice, queue ownership, iterator and data-location constraints, synchronization, algorithm migration, stable-order requirements, and serial-reference validation.

Why this helps: agents are prompted to prove policy, iterator, lifetime, and ordering contracts before presenting a device migration as correct.

The initial ask is a 30–45 minute accuracy review and a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-onedpl/SKILL.md`
- Official sources: `skills/uxl-onedpl/references/official-sources.md`
- Prompt evals: `skills/uxl-onedpl/evals/evals.json`
- Public card: `skill-cards/uxl-onedpl.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-onedpl`)

Coverage state: 4 of 6 declared tasks implemented; 1 discriminating task retains measured headroom; 2 live tasks are sourced from maintainer incidents. Planned coverage still needs a host-versus-device selection task and a transfer-inclusive benchmark. Sources were last checked on 2026-08-12 and should be refreshed during review.

## Suggested reviewers

Please route to current oneDPL maintainers responsible for algorithms/execution policies, device backends, validation, and documentation. No individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Execution-policy, queue, iterator, synchronization, and ordering guidance is correct.
- [ ] Device/backend and algorithm-support limitations are stated neutrally.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
