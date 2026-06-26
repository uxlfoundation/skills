# uxl-onetbb Skill Card

## Status

- Status: incubating
- Owner project: oneTBB
- Target source of truth: `uxlfoundation/oneTBB` after maintainer review
- Maintainer review: needed

## Purpose

Guide agents through oneTBB pattern selection, shared-state analysis, grainsize decisions, flow graph and pipeline choices, arenas, global controls, and oversubscription triage.

## Supported Tasks

- Choose between `parallel_for`, reductions, scans, pipelines, flow graph, and task groups.
- Review shared mutable state and race risks.
- Diagnose nested parallelism and oversubscription issues.
- Require serial correctness and realistic CPU benchmarks.

## Limitations

- Does not replace the oneTBB API reference.
- Needs maintainer review for migration guidance from legacy TBB.
- Does not cover GPU offload; route those tasks to SYCL or oneDPL skills.

## Evidence

- Source ledger: `skills/uxl-onetbb/references/official-sources.md`
- Evals: `skills/uxl-onetbb/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
