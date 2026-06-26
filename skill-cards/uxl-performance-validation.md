# uxl-performance-validation Skill Card

## Status

- Status: incubating
- Owner project: UXL cross-project
- Target source of truth: central catalog
- Maintainer review: needed

## Purpose

Guide agents through correctness-first performance validation: baselines, representative problem sizes, synchronization, timing scope, tolerances, benchmark reporting, and conservative performance claims.

## Supported Tasks

- Review unsupported performance claims.
- Design benchmark plans and result tables.
- Handle floating point tolerance and non-associativity.
- Summarize benchmark CSV output.

## Limitations

- Does not run vendor profilers directly.
- Requires project-specific benchmarks for authoritative claims.
- Needs maintainer review from performance owners.

## Evidence

- Source ledger: `skills/uxl-performance-validation/references/official-sources.md`
- Benchmark contract: `skills/uxl-performance-validation/references/benchmark-contract.md`
- Evals: `skills/uxl-performance-validation/evals/evals.json`
- Script: `skills/uxl-performance-validation/scripts/summarize_runs.py`
- Validation: catalog validator and skill quick validation pass locally.
