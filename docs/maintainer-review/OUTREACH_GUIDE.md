# Maintainer outreach guide

## The first-minute message

UXL Skills are small, project-specific instruction packages that help coding agents follow a repository's real engineering practice. Each skill links to official sources and is tested on realistic tasks with the same model, harness, task, and environment across no-skill, previous-skill, and candidate-skill arms.

The maintainer value is fewer repeated corrections: agents are prompted to use the project's supported APIs, debugging evidence, validation tools, and limitation language before they propose a change. UXL maintains the shared evaluator and dashboard. Project teams decide whether their guidance is accurate and who should approve changes.

## What exists now

| Skill | First-use value | Current evaluator coverage |
| --- | --- | --- |
| oneCCL | Collective contracts, async completion, launch symmetry, hang triage | 5 of 7 tasks implemented; 2 with headroom |
| oneDAL | Interface/mode choice, tables, parity, conversion cost | 5 of 6; 1 with headroom |
| oneDNN | Primitives, layouts, post-ops, verbose and `benchdnn` evidence | 5 of 6; 1 with headroom |
| oneDPL | Policies, iterators, queue/lifetime, synchronization, ordering | 4 of 6; 1 with headroom |
| oneMath | Dispatch, queues, build/link, backend integration | 3 of 6; 1 with headroom |
| oneTBB | Patterns, flow graphs, cancellation, arenas, oversubscription | 7 of 7; 2 with headroom |
| SYCL build/debug | Cross-project compiler, linker, loader, runtime, device triage | 8 of 8; 1 with headroom |
| Performance validation | Correctness-gated measurement and conservative claims | 4 of 6; no current headroom claim |

These numbers describe evaluator coverage, not project quality. Planned tasks and no-lift results remain visible.

## The small decision we need

Ask reviewers to do four things:

1. Correct or reject inaccurate scope, procedures, limitations, and task scenarios.
2. Nominate one recurring maintainer failure that would distinguish useful guidance.
3. Choose ownership: project-local source of truth after review, or periodic review of the central catalog.
4. Name a reviewer for future material changes. UXL continues to operate the common evaluator and dashboard.

Do not ask a project to approve a universal benchmark score, support every model, operate hardware, or guarantee agent behavior.

## Likely questions

**How can you test every model, harness, version, and device?**  We do not claim an exhaustive matrix. Each matched evaluation cell records its exact task, skill, model, harness, reasoning effort, software, environment, hardware class, and attempt count. Material changes make that claim stale and trigger targeted reruns. Evidence from incompatible cells is shown separately, not averaged into one universal score.

**Will the skill become stale documentation?**  It is procedural guidance with a source ledger and refresh date, not a copied API reference. Release-dependent claims must point back to current project sources. Maintainers can reject scope that would create high upkeep.

**Is this benchmarking the project?**  No. Evaluator states describe whether a task reveals useful agent guidance. They do not score library health, hardware quality, or maintainer performance.

**Will one vendor's hardware define success?**  No. Hosted CPU is the default. Specialized machines are adapters for tasks that genuinely require them, and hardware is a recorded dimension. A result on one lane is not silently generalized to another.

**Can an agent game a prompt-specific test?**  Promotion uses repeated matched arms, exact verifier source, retained trajectories/artifacts, and maintainer-backed incidents where possible. Reviewers can reject synthetic or unrealistic tasks.

**What maintenance burden lands on the project?**  The requested burden is content review and approval of material changes. UXL owns the shared schema, runner integration, dashboard, and portfolio checks unless a project explicitly chooses otherwise.

**What happens if a skill does not help?**  We record no lift, revise the task or guidance only with evidence, or stop the skill. A negative result is a valid outcome.

## Suggested review sequence

1. Send the project-specific deck and one-page packet.
2. Review `SKILL.md` and its limitations before discussing scores.
3. Inspect one representative task, verifier, and trajectory.
4. Record `approved`, `changes requested`, or `ownership declined` in the packet.
5. Update skill, sources, evals, card, catalog metadata, and accepted evidence together.
