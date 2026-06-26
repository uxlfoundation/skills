# uxl-oneccl Skill Card

## Status

- Status: incubating
- Owner project: oneCCL
- Target source of truth: `uxlfoundation/oneCCL` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneCCL collective selection, communicator setup, launch symmetry, plugin/environment settings, async wait semantics, framework integration, and hang triage.

## Supported Tasks

- Triage distributed collectives that hang.
- Review async collective completion semantics.
- Choose API path with current documentation checks.
- Separate correctness fixes from transport/plugin tuning.

## Limitations

- Does not encode every environment variable or plugin option.
- Needs current upstream verification for C API, GPU, framework, and plugin behavior.
- Needs maintainer review for distributed launch recommendations.

## Evidence

- Source ledger: `skills/uxl-oneccl/references/official-sources.md`
- Evals: `skills/uxl-oneccl/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
