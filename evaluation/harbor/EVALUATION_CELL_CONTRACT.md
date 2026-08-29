# Matched evaluation-cell contract

An evaluation cell is the smallest scope in which UXL makes a skill-quality claim. The no-skill, previous-skill, and candidate-skill arms differ only in skill treatment. They share the task and verifier revision, agent and harness, model and reasoning effort, execution environment, attempts, timeout, and concurrency.

The machine-readable record uses [`schemas/evaluation-cell.schema.json`](../../schemas/evaluation-cell.schema.json). Validate a record with:

```powershell
python scripts/validate_evaluation_cell.py <evaluation-cell.json>
```

To check whether historical evidence is still current, supply a record-shaped snapshot containing the current material dimensions:

```powershell
python scripts/validate_evaluation_cell.py <evaluation-cell.json> `
  --current-context <current-context.json> `
  --fail-if-stale
```

## Validity rules

- Development uses at least one accepted attempt per arm, calibration uses at least three, and promotion uses at least five.
- Every arm must complete the same accepted-attempt count without errors. Infrastructure failures are counted separately, excluded, and rerun unchanged.
- Promotion evidence must use immutable task and skill revisions with clean task and candidate trees.
- Specialized hardware cells require a digest of the non-secret qualification probe.
- Tokens, cost, and runtime are interpreted only after the verified-success quality gate.

## Freshness rules

Each record declares its maximum age and material dimensions. A result becomes stale for current-proof purposes when the age limit is exceeded or a declared dimension changes. It remains historical evidence and is never silently rewritten.

Every v1 cell declares task and verifier content, skill content, model, harness, reasoning effort, image, toolchain, OS, hardware qualification, attempts, timeout, and concurrency as material dimensions. Git commits remain immutable provenance identifiers, while content digests decide whether a task or skill changed; an unrelated repository commit does not invalidate evidence. Incompatible cells are reported separately, and their rewards are not averaged into a universal score.

## Retained ledger and dashboard

The comparison wrapper emits `<prefix>-evaluation-cell.json` beside its Markdown report. After reviewing the cell with its raw Harbor jobs, copy only an accepted, sanitized record to `evaluation/harbor/results/cells/<cell_id>.json`. CI validates the ledger, and the public UXL Skills Evaluator exposes summary fields and source links while raw trajectories and private-machine provenance remain access-controlled.
