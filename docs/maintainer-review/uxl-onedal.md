# oneDAL skill maintainer review

Review state: not requested

Reviewed commit: pending

## Review request

Please review `uxl-onedal` for technical accuracy, useful scope, honest limitations, and suitability as a oneDAL-maintained coding-agent skill.

The current skill covers native oneDAL versus Extension for Scikit-learn, batch/online/distributed mode choice, table layout, analytics parity, conversion costs, and quality-regression triage. It requires algorithm-, interface-, version-, and device-specific support checks.

Why this helps: agents get oneDAL-specific interface, table, mode, and quality checks before proposing code, reducing generic scikit-learn or device assumptions that maintainers must correct later.

The initial ask is a 30–45 minute accuracy review and a decision on periodic ownership—not a commitment to support the evaluator infrastructure.

## Evidence to inspect

- Instructions: `skills/uxl-onedal/SKILL.md`
- Official sources: `skills/uxl-onedal/references/official-sources.md`
- Prompt evals: `skills/uxl-onedal/evals/evals.json`
- Public card: `skill-cards/uxl-onedal.md`
- Harbor matrix: `evaluation/harbor/suites.json` (`uxl-onedal`)

Coverage state: 5 of 6 declared tasks implemented; 1 discriminating task retains measured headroom; 1 live task is sourced from a maintainer incident. The remaining planned task needs an authentic unavailable-GPU-path case on a declared target. Current sources were rechecked on 2026-08-25 against `2026.1.0`.

## Suggested reviewers

The current project ownership files identify architecture maintainers `@Vika-F`, `@Alexandr-Solovev`, and `@Alexsandruss`; release maintainers `@napetrov`, `@syakov-intel`, and `@maria-Petrova`; and documentation/platform owner teams. These are candidate reviewer teams only; no individual has been assigned or contacted by this repository.

## Decision checklist

- [ ] Scope and trigger description are accurate.
- [ ] Interface, computation-mode, and table-layout guidance reflects supported practice.
- [ ] GPU, algorithm-coverage, and DAAL-migration limitations are stated correctly.
- [ ] Source ledger is sufficient and current.
- [ ] Eval prompts and Harbor tasks are realistic and balanced.
- [ ] A project team is willing to own or periodically review the skill.

Decision: pending

Reviewer/date: pending

Required changes: pending
