# UXL Skills weekend checkpoint — 2026-08-29

The initial planned repository work and the first weekend continuation are complete on `weekend/evaluation-cells-target-adapters`.

## Delivered

- A strict matched evaluation-cell contract records task, verifier, skill revisions, model, harness, software, environment, hardware qualification, attempts, results, and staleness dimensions.
- The Harbor comparison wrapper emits the human report and machine-readable cell together. CI validates retained cells, and the public dashboard exposes sanitized evidence summaries.
- Evidence freshness is content-aware: task, verifier, and skill directory digests detect material changes, while Git commits remain immutable provenance instead of invalidating unrelated cells.
- The dashboard now shows current, age-expired, and repository-changed cells plus the exact tested configuration matrix. It reports the empty v1 ledger explicitly instead of implying historical reports are current proof.
- A vendor-neutral specialized-target adapter adds a reviewed private dispatcher, immutable revision gate, host probes, reward-1.0 oracle, common artifact layout, tests, and exact setup guide.
- Private target workflows accept only evaluator commits reachable from public `main` or explicitly listed in a reviewed private allowlist. Raw probe logs stay access-controlled; public provenance retains their digest by default.
- All eight skills have concise maintainer review packets. A shared outreach guide covers the first-minute value statement, ownership ask, and expected questions about models, harnesses, versions, hardware, maintenance, and negative results.
- A migration audit found no complete historical three-arm artifact set with the exact v1 provenance. No evidence cell was synthesized from incomplete Markdown reports.
- Specialized-lane health now has its own strict public contract and ledger. The existing GLOW Windows/WSL oracle is represented by one sanitized, expiring qualification record; raw probes and private runner identity remain access-controlled.
- The generic target adapter emits the same sanitized record only after a clean immutable task passes its reward-1.0 oracle.
- Repository content digests now use Git-filtered content, excluding ignored build artifacts and normalizing line endings across Windows and Linux runners.
- Artifact import now validates proposed qualification records against their exact Harbor result and runner-provenance hashes, then stages only the sanitized candidate for manual publication review.

## Validation

- Catalog, 33 prompt evals, 8 Harbor suites, 52 declared tasks, generated matrix, structured checkers, and retained-cell ledger passed.
- 98 repository tests passed; 2 optional dependency tests were skipped.
- The public dashboard passed generated-data drift checks, lint, static build, and rendered-page tests.
- Desktop and mobile browser review passed for evidence-cell and specialized-lane health with no console warnings.
- The comparison wrapper passed PowerShell parsing and an end-to-end three-arm dry run.
- Local links and 125 external links passed validation.

## Remaining human or external gates

- No v1 matched evidence cell has been accepted yet; the dashboard reports zero structured records honestly.
- One specialized lane qualification is current through 2026-11-23; no second vendor or laboratory lane has been qualified.
- No maintainer has been contacted or represented as approving a skill.
- A new vendor/lab target still needs its machine-specific adapter JSON, labels, probe commands, runtime, and oracle task.
- The branch has not been pushed and no pull request or release has been created.

## Recommended next actions

1. Review and push the checkpoint commits, then open one PR.
2. Run the first calibration cell on a hosted task and retain its sanitized JSON.
3. Configure a second specialized target from `docs/target-device-adapter.md`, then retain its generated sanitized qualification record to prove portability beyond GLOW.
4. Assign human owners and send the prepared oneTBB, oneDNN, and oneDAL review packets first.
