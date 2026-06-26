# uxl-onedal Skill Card

## Status

- Status: incubating
- Owner project: oneDAL
- Target source of truth: `uxlfoundation/oneDAL` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneDAL native C++ versus scikit-learn acceleration choices, batch/online/distributed mode selection, data table layout, metrics parity, and performance validation.

## Supported Tasks

- Choose Extension for Scikit-learn versus native oneDAL APIs.
- Review distributed-mode proposals.
- Debug model quality changes after table conversion.
- Require metric and preprocessing parity before performance tuning.

## Limitations

- Does not encode full algorithm coverage.
- Needs current upstream verification for GPU and algorithm support.
- Needs maintainer review for oneAPI versus DAAL migration nuance.

## Evidence

- Source ledger: `skills/uxl-onedal/references/official-sources.md`
- Evals: `skills/uxl-onedal/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
