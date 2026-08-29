# UXL Skills weekend checkpoint — 2026-08-29

The planned repository work is complete on `weekend/evaluation-cells-target-adapters`.

## Delivered

- A strict matched evaluation-cell contract records task, verifier, skill revisions, model, harness, software, environment, hardware qualification, attempts, results, and staleness dimensions.
- The Harbor comparison wrapper emits the human report and machine-readable cell together. CI validates retained cells, and the public dashboard exposes sanitized evidence summaries.
- A vendor-neutral specialized-target adapter adds a reviewed private dispatcher, immutable revision gate, host probes, reward-1.0 oracle, common artifact layout, tests, and exact setup guide.
- All eight skills have concise maintainer review packets. A shared outreach guide covers the first-minute value statement, ownership ask, and expected questions about models, harnesses, versions, hardware, maintenance, and negative results.

## Validation

- Catalog, 33 prompt evals, 8 Harbor suites, 52 declared tasks, generated matrix, structured checkers, and retained-cell ledger passed.
- 84 repository tests passed; 2 optional dependency tests were skipped.
- The public dashboard passed generated-data drift checks, lint, static build, and rendered-page tests.
- The comparison wrapper passed PowerShell parsing and an end-to-end three-arm dry run.
- Internal links passed. External HTTP validation was deferred to CI because this workstation's Python certificate chain rejected all HTTPS hosts during the local check.

## Remaining human or external gates

- No v1 matched evidence cell has been accepted yet; the dashboard reports zero structured records honestly.
- No maintainer has been contacted or represented as approving a skill.
- A new vendor/lab target still needs its machine-specific adapter JSON, labels, probe commands, runtime, and oracle task.
- The branch has not been pushed and no pull request or release has been created.

## Recommended next actions

1. Review and push the four checkpoint commits, then open one PR.
2. Run the first calibration cell on a hosted task and retain its sanitized JSON.
3. Configure a second specialized target from `docs/target-device-adapter.md` to prove portability beyond GLOW.
4. Assign human owners and send the prepared oneTBB, oneDNN, and oneDAL review packets first.
