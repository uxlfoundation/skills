# uxl-onednn Skill Card

## Status

- Status: incubating
- Owner project: oneDNN
- Target source of truth: `uxlfoundation/oneDNN` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneDNN primitive selection, memory descriptors, graph/fusion choices, post-ops, backend assumptions, numerical parity, and `benchdnn` validation.

## Supported Tasks

- Plan or review oneDNN primitive integrations.
- Triage layout and reorder-related performance regressions.
- Separate correctness validation from performance claims.
- Point agents to official docs and `benchdnn` references.

## Limitations

- Does not encode every primitive option or backend support table.
- Requires current upstream verification for latest releases and hardware support.
- Needs oneDNN maintainer review before promotion.

## Evidence

- Source ledger: `skills/uxl-onednn/references/official-sources.md`
- Evals: `skills/uxl-onednn/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
