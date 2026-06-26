# uxl-sycl-build-debug Skill Card

## Status

- Status: incubating
- Owner project: UXL cross-project
- Target source of truth: central catalog
- Maintainer review: needed

## Purpose

Guide agents through cross-project SYCL build and runtime triage: compiler selection, CMake configuration, target backend flags, linking, runtime loader paths, device discovery, and queue selection.

## Supported Tasks

- Classify configure, compile, link, runtime load, and device discovery failures.
- Generate a safe local SYCL toolchain report.
- Keep compiler, backend, package, and runtime hypotheses separate.
- Route library-specific issues back to the relevant UXL skill.

## Limitations

- The probe script reports local evidence but does not install toolchains.
- Current backend support must be checked in upstream docs.
- Needs review from maintainers across projects that use SYCL.

## Evidence

- Source ledger: `skills/uxl-sycl-build-debug/references/official-sources.md`
- Evals: `skills/uxl-sycl-build-debug/evals/evals.json`
- Script: `skills/uxl-sycl-build-debug/scripts/sycl_probe.py`
- Validation: catalog validator and skill quick validation pass locally.
