# oneTBB skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-onetbb` for technical accuracy, useful scope, honest limitations, and suitability as a oneTBB-maintained coding-agent skill.

The current skill covers pattern selection, shared-state and ordering analysis, grainsize and affinity, flow graphs, cancellation, arenas, global controls, and oversubscription triage. It explicitly routes GPU offload to SYCL or oneDPL guidance.

Why this helps: agents get oneTBB-specific decision and debugging discipline at the moment they edit a oneTBB codebase, while maintainers retain control over the guidance and its tests.

The initial ask is a 30–45 minute accuracy review and a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-onetbb/SKILL.md`
- Official sources: `skills/uxl-onetbb/references/official-sources.md`
- Prompt evals: `skills/uxl-onetbb/evals/evals.json`
- Public card: `skill-cards/uxl-onetbb.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-onetbb`)

Coverage state: 7 of 7 declared tasks implemented; 2 discriminating tasks retain measured headroom; 1 live task is sourced from a maintainer incident. Current sources were rechecked on 2026-08-25 against `v2023.1.0`.

## Suggested reviewers

The current project ownership files identify the core maintainer team (`@kboyarinov`, `@aleksei-fedotov`, `@vossmjp`, `@dnmokhov`) and documentation owners (`@aepanchi`, `@omalyshe`). These are candidate reviewer teams only; no individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Procedural guidance reflects supported oneTBB practice.
- [ ] Legacy-TBB migration and GPU limitations are stated correctly.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
