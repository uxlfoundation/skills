# oneCCL skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-oneccl` for technical accuracy, useful scope, honest limitations, and suitability as a oneCCL-maintained coding-agent skill.

The skill covers collective selection, communicator and launch symmetry, async completion, buffer/count contracts, plugin boundaries, framework integration, and hang triage. It separates correctness from transport tuning and requires current upstream checks for APIs, devices, and plugins.

Why this helps: agents receive oneCCL-specific preflight and hang-triage guidance before guessing at transport settings or treating asynchronous work as complete.

The initial ask is a 30–45 minute accuracy review, one realistic recurring failure, and a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-oneccl/SKILL.md`
- Official sources: `skills/uxl-oneccl/references/official-sources.md`
- Prompt evals: `skills/uxl-oneccl/evals/evals.json`
- Public card: `skill-cards/uxl-oneccl.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-oneccl`)

Coverage state: 5 of 7 declared tasks implemented; 2 tasks retain measured headroom; the zero-count `alltoallv` fixture follows issue #174 and its accepted repair but does not reproduce the original Aurora/Level Zero environment. Two planned tasks still need realistic plugin visibility and worker-affinity cases. Incident sources were rechecked on 2026-08-27.

## Suggested reviewers

Please route to the current oneCCL core maintainer team plus the transport/plugin or framework-integration owners relevant to the selected incident. No individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Collective, completion, launch, and buffer guidance reflects supported practice.
- [ ] API, plugin, framework, and device limitations are stated neutrally.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
