# UXL skills project roadmap — 2026 H2

## Outcome

Move the catalog from a strong incubating evaluator into a maintainer-reviewed, project-owned distribution system, while using the same evidence machinery to establish whether UXL has a defensible role in agentic AI pipelines.

The project should pursue two connected tracks:

1. **Catalog maturity:** finish representative executable coverage, obtain maintainer review, and promote the strongest skills.
2. **Agentic proof point:** build one benchmark-led integration that demonstrates measurable UXL value in an existing Python agent framework.

The tracks share the same contract: correctness first, matched baseline/candidate trials, retained artifacts, current official sources, and no unsupported performance claims.

## Current position

- Eight skills are published, but seven remain `incubating` and one remains `pilot`.
- All skills still require owning-project maintainer review.
- The Harbor portfolio has meaningful coverage, but oneMath, oneDPL, oneCCL, SYCL, and performance validation still have planned tasks.
- oneCCL and SYCL lack a real end-to-end maintainer-incident or upstream-regression task.
- Target-device and distributed evidence remains the largest promotion gap.
- The [agentic plan](agentic-plan.md) supplies a two-quarter strategy, but its reference workload and first pilot have not yet been implemented.

## Phase 1 — stabilize and choose (weeks 1–4)

### Catalog

1. Freeze the current schema and promotion policy for one release cycle.
2. Run the complete validation suite and record one clean release-candidate ledger entry.
3. Rank open Harbor tasks by promotion impact:
   - real end-to-end incident tasks for oneCCL and SYCL;
   - target-device tasks for oneMath and oneDPL;
   - remaining performance-validation discriminating coverage;
   - lower-priority incremental smoke coverage.
4. Prepare one-page maintainer review packets for oneTBB, oneDNN, and oneDAL, which currently have the strongest implemented coverage.
5. Assign an owner and review date for every `maintainer_review: needed` entry.

### Agentic track

1. Select one Python framework integration target.
2. Define a tool-using retrieval-agent reference workload with three shapes: short-turn, tool-fan-out, and retrieval-heavy.
3. Freeze correctness checks and stage-level timing boundaries before optimization.
4. Record baseline install time, dependency size, task success, p50/p95 latency, and cost per verified success.
5. Choose between the oneTBB scheduling pilot and oneDAL retrieval pilot using measured end-to-end contribution; do not start both by default.

### Exit criteria

- A published release-candidate evidence ledger exists.
- Three maintainer review meetings are scheduled with named owners.
- The agentic workload, baseline, and pilot-selection decision are reproducible.

## Phase 2 — close evidence gaps (weeks 5–10)

### Catalog

1. Implement the highest-impact missing executable tasks.
2. Source oneCCL and SYCL tasks from maintainer incidents or upstream regressions.
3. Run matched no-skill, previous-skill, and candidate-skill trials with at least three attempts during calibration.
4. Repair tasks that show ceiling or no-lift behavior when they cannot distinguish useful agent behavior.
5. Exercise the Windows/WSL Intel GPU lane only after its separate task and workflow contract are reviewed.

### Agentic track

1. Build a thin, pip-installable prototype at an existing framework extension point.
2. Add Harbor tasks covering successful execution, cancellation/failure behavior, fallback, and a negative control.
3. Measure framework overhead, conversion costs, synchronization, and packaging—not only kernel time.
4. Stop the pilot if it cannot improve an end-to-end metric or produce a credible developer-experience advantage.

### Exit criteria

- Every promotion candidate has at least one discriminating task with demonstrated headroom.
- The selected agentic pilot passes correctness and failure-path tests.
- A go/no-go evidence review decides whether to harden, redirect, or stop the pilot.

## Phase 3 — review and promote (weeks 11–16)

1. Incorporate maintainer feedback into skill instructions, source ledgers, evals, and skill cards together.
2. Recheck official sources after feedback.
3. Run five matched attempts per arm for promotion evidence.
4. Promote only skills satisfying the repository policy; likely first candidates are oneTBB, oneDNN, and oneDAL, subject to maintainer review and final trials.
5. Move project-specific source-of-truth skills into owning repositories and retain this catalog as the reviewed distribution mirror.
6. If the agentic pilot passes its gate, publish its benchmark, integration guide, limitations, and project ownership proposal.

## Phase 4 — scale what worked (weeks 17–24)

- Extend agentic coverage to a second UXL library only after the first integration is reproducible and maintainable.
- Turn measured short-prefill, decode, conversion, scheduling, or communication gaps into project-owned issues.
- Create `uxl-agentic-pipeline` only when a supported cross-project workflow exists; do not publish a speculative umbrella skill.
- Establish a quarterly source-verification and paired-evaluation cadence.
- Retire or narrow skills and tasks that do not improve agent behavior or no longer reflect supported project paths.

## Next ten working days

| Priority | Deliverable | Owner | Evidence of completion |
| --- | --- | --- | --- |
| 1 | Release-candidate validation ledger | Catalog owner | all required checks recorded against one commit |
| 2 | oneTBB, oneDNN, and oneDAL maintainer packets | Skill owners | sources, limitations, task matrix, and review dates |
| 3 | oneCCL and SYCL incident requests | Project liaisons | accepted incident or regression candidates |
| 4 | Agentic reference-workload contract | Agentic working-group lead | fixture, correctness oracle, timing schema, baseline command |
| 5 | Framework and pilot selection | Steering group | documented decision with measured rationale |
| 6 | Artifact retention cleanup | Evaluator owner | retained jobs indexed by commit/task/model; disposable runs removed |

## Operating cadence

- Weekly: task implementation, evaluator health, and infrastructure blockers.
- Monthly: maintainer review status, source freshness, promotion scorecard, and agentic pilot evidence.
- Per release: full validation, link check, wrapper drift check, retained Harbor evidence, and release ledger.
- Per performance claim: correctness gate, declared environment, matched baseline, repeated timings, and bounded conclusion.

## Decisions needed now

1. Name the three initial maintainer-review owners.
2. Select the agent framework used for the reference workload.
3. Choose the two hardware environments used for baseline and pilot evidence.
4. Decide whether the next release optimizes for first skill promotion or broader task coverage. The recommended choice is first promotion: it tests the complete governance path and exposes the real review bottlenecks sooner.
