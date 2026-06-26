# uxl-onedpl Skill Card

## Status

- Status: incubating
- Owner project: oneDPL
- Target source of truth: `uxlfoundation/oneDPL` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneDPL algorithm migration, host versus device execution policies, SYCL queue ownership, iterator/data movement constraints, synchronization, and correctness testing.

## Supported Tasks

- Choose host policy versus SYCL device policy.
- Debug missing device synchronization or data lifetime issues.
- Port standard algorithms to oneDPL with serial reference checks.
- State device/backend assumptions explicitly.

## Limitations

- Does not mirror full algorithm support tables.
- Needs current upstream verification for device policy behavior and GPU backends.
- Needs maintainer review for current CI and validation expectations.

## Evidence

- Source ledger: `skills/uxl-onedpl/references/official-sources.md`
- Evals: `skills/uxl-onedpl/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
