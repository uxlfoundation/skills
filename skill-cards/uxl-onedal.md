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
- Select batch, online, or distributed computation from data arrival, memory, and launch topology.
- Debug model quality changes after table conversion.
- Detect orientation bugs hidden by square fixtures with rectangular-shape and metric-parity checks.
- Require metric and preprocessing parity before performance tuning.

## Limitations

- Does not encode full algorithm coverage.
- Needs current upstream verification for GPU and algorithm support.
- Mode advice is workload-level; exact mode availability must still be checked for the algorithm, interface, version, and device.
- Needs maintainer review for oneAPI versus DAAL migration nuance.

## Evidence

- Source ledger: `skills/uxl-onedal/references/official-sources.md`
- Evals: `skills/uxl-onedal/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
