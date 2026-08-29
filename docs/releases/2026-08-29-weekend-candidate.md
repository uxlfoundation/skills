# 2026-08-29 Weekend release-candidate ledger

Candidate commit: `0aced9da65537d53a9999cd327fc72bf1415a576`

Base commit: `ed69e5bd0806bf007d72b4b72297ed93a510f5f9` (`origin/main`)

Branch: `weekend/evaluation-cells-target-adapters` — 10 local commits ahead of the recorded base

Release type: local, unpushed review candidate

## Review scope

- Matched evaluation cells now retain exact task, verifier, skill, model, harness, software, environment, hardware, attempt, and result dimensions. Content-aware health distinguishes current evidence from age-expired or repository-changed evidence.
- A vendor-neutral specialized-target adapter qualifies one immutable task on a controlled machine, emits private diagnostics, and proposes a sanitized public qualification only after a reward-1.0 oracle pass.
- The public GitHub Pages dashboard exposes evidence-cell and specialized-lane health without exposing runner names, raw probes, local paths, trajectories, credentials, or private URLs.
- The private-artifact importer verifies qualification schema plus exact result/provenance hashes and stages the sanitized candidate for human review. It never publishes automatically.
- The private WSL runner launcher accepts only a private control repository, uses an ephemeral registration, and now resumes a matching offline registration after a host reboot while refusing ambiguous state.
- All eight project review packets now contain the first-use value, current skill contents, evaluator coverage, ownership decision, and concise responses to expected maintainer questions.

## Recorded validation

The candidate content passed locally on 2026-08-29:

- catalog validation and 33 prompt-eval definitions;
- 8 Harbor suites, 52 declared tasks, and 41 implemented tasks;
- 0 retained v1 matched evaluation cells and 1 valid sanitized target qualification;
- generated capability matrix, 11 structured-answer checkers, and 12 agent wrappers;
- 99 repository tests, with 2 optional dependency tests skipped;
- dashboard generated-data drift check, lint, static export, and 5 rendered-page tests;
- desktop and mobile browser review with no console warnings; and
- local links plus 125 external links.

The GLOW registration was exercised through the real reboot-recovery path and observed online and idle in the private control repository at 2026-08-29T05:51:33Z. Runner availability is transient operational state, not a release guarantee.

## Evidence boundaries

- The existing GLOW Windows/WSL Intel GPU record qualifies one lane, task, device configuration, and time window. It does not establish skill benefit, cross-vendor portability, or a performance claim.
- The empty evaluation-cell ledger is intentional. Historical Markdown reports lack the complete v1 provenance and were not converted into stronger evidence than they contain.
- The 11 remaining planned tasks require an authentic maintainer incident or an appropriate target-device/distributed lane. They remain visible rather than being replaced with synthetic evidence.

## Gates still open

- The branch has not been pushed; no pull request, release, or deployment was created from it.
- No project maintainer has been contacted or represented as approving a skill.
- No v1 matched evaluation cell has been accepted into the public ledger.
- No second vendor or laboratory target has been qualified.
- Promotion trials still require the selected model, credentials, matched arms, retained artifacts, and the policy attempt count.

## Recommended review order

1. Review the evaluation-cell and qualification schemas, validators, and privacy contracts.
2. Review the private runner trust boundary and immutable-revision controls.
3. Build the dashboard and inspect the empty/current/stale states.
4. Review oneTBB, oneDNN, and oneDAL maintainer packets before approving outreach.
5. Push the branch and open one pull request only after the local candidate is accepted.
