# uxl-onednn Skill Card

## Status

- Status: incubating
- Owner project: oneDNN
- Target source of truth: `uxlfoundation/oneDNN` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneDNN primitive selection, memory descriptors, graph/fusion choices, post-ops, backend assumptions, numerical parity, verbose implementation evidence, and `benchdnn` validation.

## Supported Tasks

- Plan or review oneDNN primitive integrations.
- Triage layout and reorder-related performance regressions.
- Classify `benchdnn` failures by mode and by create, fill, execute, compare, or report phase.
- Separate correctness validation from performance claims.
- Validate fused post-op order and preserve sum inputs in the primitive-selected destination layout.
- Point agents to official docs and `benchdnn` references.

## Limitations

- Does not encode every primitive option or backend support table.
- Requires current upstream verification for latest releases and hardware support.
- Needs oneDNN maintainer review before promotion.

## Evidence

- Source ledger: `skills/uxl-onednn/references/official-sources.md`
- Evals: `skills/uxl-onednn/evals/evals.json`
- Official sources and project ownership files rechecked on 2026-08-25 against release `v3.13.1`.
- Live evaluators: `onednn-benchdnn-no-ref-memory`, sourced from oneDNN issue #5732, and the constructed `onednn-convolution-fusion-parity` CPU task.
- Validation: catalog validator, Harbor task validation, and skill quick validation pass locally.
