# Maintainer incident sourcing: wave 3

This wave promoted the oneTBB cgroup CPU-quota incident into deterministic hosted-CPU coverage for `uxl-performance-validation`. The task tests resource triage, not device-specific performance: it verifies that effective oneTBB concurrency respects a container CPU-time quota even when the schedulable CPU mask remains wider.

## Incident and reproducibility gate

The source incident is [oneTBB #1760](https://github.com/uxlfoundation/oneTBB/issues/1760), fixed by [PR #1777](https://github.com/uxlfoundation/oneTBB/pull/1777). The accepted upstream change is commit `aea8ce893c8ec758db604292edd3c031f513c057`; its immediate pre-fix parent is `ee718990c2c91dac7bc064b2c23a4fb0f579840f`.

Both revisions were built from exact local archives with the same compiler and probe. Docker supplied a cgroup v2 quota without narrowing the CPU mask.

| Revision | Schedulable CPUs | `cpu.max` | `task_arena` concurrency | Repetitions |
| --- | ---: | --- | ---: | ---: |
| Pre-fix `ee718990…` | 8 | `200000 100000` | 8 | 10/10 identical |
| Fixed `aea8ce89…` | 8 | `200000 100000` | 2 | 10/10 identical |

The fixed revision also mapped quotas of 1, 1.5, and 3 CPUs to arena concurrency 1, 2, and 3. The verifier therefore uses state rather than throughput and can reject a repair that hardcodes the visible two-CPU quota.

## Implemented task

`performance-cgroup-concurrency-quota` is a minimized application-level reproduction of the incident. It uses real oneTBB `task_arena` execution and the live cgroup v2 `cpu.max` file, but keeps the allowed repair surface to one source file. The starting application incorrectly equates schedulable CPUs with its CPU-time budget and explicitly constructs an over-wide arena. The repair must derive a dynamic quota-aware limit, preserve an unconstrained fallback, and keep a deterministic parallel checksum correct.

This minimization does not claim to reimplement or test every path in the upstream runtime patch. It preserves the maintainer-reported failure contract while making alternative correct application repairs reviewable in Harbor.

| Check | Result |
| --- | ---: |
| Direct baseline | Reward 0 |
| Direct oracle | Reward 1 |
| Harbor oracle | Reward 1; 1 trial, 0 exceptions |
| Full hosted oracle suite | 22 of 22 trials at reward 1; 0 exceptions |
| Live quota | Numeric cgroup v2 quota, generic hosted CPU |
| Hidden cases | Integer, fractional, unconstrained, malformed, missing, zero, extra-field, and overflow inputs |
| Performance timing | None; deterministic concurrency state and correctness only |

## Skill effect and portfolio impact

The performance skill now tells agents to distinguish CPU affinity from cgroup quota and to inspect effective oneTBB arena concurrency before timing. It prefers a cgroup-aware runtime over hardcoded limits. This is hardware-agnostic resource guidance: no CPU model, GPU, backend, or target-specific speed threshold is required.

The portfolio remains 49 planned tasks and now has 23 implemented tasks. Three implemented tasks meet the full live reproduce/investigate/repair/verify and maintainer-incident standard: `onetbb-join-node-ordering`, `onemath-deprecated-header-include`, and `performance-cgroup-concurrency-quota`.

The next gate is matched calibration of this task with no skill, the previous performance skill, and the candidate performance skill. Quality remains the gate; token usage, cost per verified success, and runtime will determine whether the new guidance improves efficiency or remains regression coverage.

Two initial Harbor attempts were preserved but excluded as infrastructure failures: WSL Docker could not reach Docker Hub metadata or Debian packages until the workstation's existing proxy was supplied to build containers. The successful retry used the identical task, solution, verifier, and pinned base image.
