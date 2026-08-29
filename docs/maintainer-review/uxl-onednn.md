# oneDNN skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-onednn` for technical accuracy, useful scope, honest limitations, and suitability as a oneDNN-maintained coding-agent skill.

The current skill covers primitive and graph choices, memory descriptors, layout boundaries, post-ops, backend assumptions, numerical parity, verbose evidence, and `benchdnn` validation. It requires current upstream verification for hardware and primitive support rather than encoding a static support table.

Why this helps: agents are directed toward oneDNN's actual layout, primitive, verbose, and `benchdnn` workflows instead of generic deep-learning advice or stale backend claims.

The initial ask is a 30–45 minute accuracy review and a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-onednn/SKILL.md`
- Official sources: `skills/uxl-onednn/references/official-sources.md`
- Prompt evals: `skills/uxl-onednn/evals/evals.json`
- Public card: `skill-cards/uxl-onednn.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-onednn`)

Coverage state: 5 of 6 declared tasks implemented; 1 discriminating task retains measured headroom; `onednn-benchdnn-no-ref-memory` is sourced from issue #5732 and accepted repair #5735. The remaining planned task needs a real target-device backend failure. Current sources were rechecked on 2026-08-25 against `v3.13.1`.

## Suggested reviewers

The current project ownership files identify core maintainers `@densamoilov`, `@dzarukin`, and `@vpirogov`, plus the documentation and relevant backend owner teams. Backend-specific review should include the applicable owner; vendor-neutral wording should not imply support where a backend owner or implementation is absent. These are candidate reviewer teams only; no individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Primitive, layout, post-op, and `benchdnn` guidance reflects supported practice.
- [ ] Backend and hardware limitations are stated correctly and neutrally.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
