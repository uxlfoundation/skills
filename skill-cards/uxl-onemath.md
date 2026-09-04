# uxl-onemath Skill Card

## Status

- Status: pilot
- Owner project: oneMath
- Target source of truth: `uxlfoundation/oneMath` after maintainer review
- Maintainer review: needed
- Last source verification: 2026-09-04

## Purpose

Guide agents through oneMath domain selection, runtime versus compile-time dispatch, backend selectors, SYCL queues, device API guidance, build/link setup, and backend compatibility checks.

## Supported Tasks

- Choose between runtime dispatch, compile-time dispatch, and RNG device API.
- Diagnose CMake, compiler, link, and backend setup issues.
- Avoid confusing oneMath with Intel oneMKL.
- Require current support matrix verification for backend claims.
- Plan third-party backend integration across headers, wrappers, CMake, and tests.

## Limitations

- Does not mirror full backend support matrices.
- Needs focused maintainer input for backend-specific gotchas.
- Performance guidance relies on cross-project validation skill.
- Release-specific backend and compiler claims still require an upstream check at answer time.

## Evidence

- Source ledger: `skills/uxl-onemath/references/official-sources.md`
- Detailed references: `usage-models.md`, `build-and-linking.md`, `backend-integration.md`, `common-failures.md`
- Evals: `skills/uxl-onemath/evals/evals.json`
- Validation: catalog validator and skill quick validation pass locally.
