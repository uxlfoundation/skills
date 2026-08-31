# Evaluation-cell migration audit — 2026-08-29

## Decision

Do not retrofit a v1 evaluation cell from the historical Markdown summaries. Retain them as historical calibration records and begin the structured ledger with the next valid matched run.

## Evidence checked

- 35 retained Markdown reports mention matched or no-skill comparisons.
- The current workstation retains three Harbor job roots: a oneCCL oracle, the 35-task oracle smoke, and the Windows/WSL GPU oracle.
- No local raw no-skill/previous-skill/candidate-skill job triplet remains for the historical model comparisons.
- Representative summaries record useful fields such as task, model, attempts, and some commits, but they do not consistently retain the exact verifier digest, candidate and previous content digests, harness/software context, container provenance, or raw result authority required by the v1 contract.

## Why no record was synthesized

A structured cell is intended to make a current, auditable claim. Reconstructing missing fields from today's checkout would mix historical outcomes with current provenance. Using the Markdown report as a substitute for the absent raw Harbor results would also make the arm-level completion, error, and verified-success fields non-auditable.

The dashboard therefore reports zero retained v1 cells. This is an explicit migration boundary, not missing data hidden as a passing status.

## Forward rule

Use `scripts/compare_harbor_skill.ps1` for every new comparison. It writes the Markdown report and validated JSON cell together. Review the raw jobs, then retain only the accepted sanitized cell under `evaluation/harbor/results/cells/<cell_id>.json`.
