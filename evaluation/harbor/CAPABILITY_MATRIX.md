# Harbor capability matrix

This file is generated from `evaluation/harbor/suites.json`. Do not edit it by hand.

## Portfolio policy

- Minimum tasks per skill: 5
- Minimum discriminating tasks per skill: 2
- Required classes: `correctness`, `selection`, `integration`, `debugging`, `performance`
- Attempts: development 1, calibration 3, promotion 5
- Comparison arms: `no-skill`, `previous-skill`, `candidate-skill`
- Full triage workflow: `reproduce` -> `investigate` -> `repair` -> `verify`
- Accepted real-world origins: `maintainer-incident`, `upstream-regression`
- Efficiency quality gate: `verified-success` at reward 1.00
- Primary efficiency metric: `total-tokens-per-verified-success`
- Infrastructure failures: `exclude-and-rerun`
- Promotion guardrails: maximum task mean regression 0.10; maximum suite mean regression 0.03

## Coverage summary

A real end-to-end task is implemented, reproduces live, performs every triage stage, and comes from a maintainer incident or upstream regression.

| Skill | Target | Implemented | Live implemented | Fixture/review implemented | Target hardware | Real end-to-end | Planned |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uxl-onednn` | 6 | 3 | 2 | 1 | 1 | 1 | 3 |
| `uxl-onemath` | 6 | 2 | 1 | 1 | 2 | 1 | 4 |
| `uxl-onedal` | 6 | 3 | 1 | 2 | 1 | 0 | 3 |
| `uxl-onetbb` | 7 | 7 | 5 | 2 | 0 | 1 | 0 |
| `uxl-onedpl` | 6 | 2 | 1 | 1 | 2 | 0 | 4 |
| `uxl-oneccl` | 6 | 3 | 1 | 2 | 2 | 0 | 3 |
| `uxl-sycl-build-debug` | 6 | 4 | 2 | 2 | 2 | 0 | 2 |
| `uxl-performance-validation` | 6 | 4 | 3 | 1 | 2 | 1 | 2 |

## uxl-onednn (oneDNN)

### Capabilities

- `primitive-contracts` (correctness): Preserve shapes, strides, data types, numerics, and memory descriptor semantics.
- `primitive-or-graph` (selection): Choose primitive, post-op, or graph paths from the required control and fusion contract.
- `framework-layout-boundaries` (integration): Integrate engines, streams, layouts, and framework-owned reorder boundaries.
- `backend-and-parity-triage` (debugging): Diagnose unsupported backends, layout errors, and numerical parity failures.
- `benchdnn-and-reorders` (performance): Use benchdnn or representative benchmarks and account for reorder costs.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `onednn-matmul-memory-descriptors` | planned | smoke | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `primitive-contracts`, `primitive-or-graph` |
| `onednn-convolution-fusion-parity` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `primitive-contracts`, `primitive-or-graph`, `backend-and-parity-triage` |
| `onednn-extra-reorder-regression` | planned | discriminating | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `framework-layout-boundaries`, `benchdnn-and-reorders` |
| `onednn-framework-blocked-layout` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `primitive-contracts`, `framework-layout-boundaries`, `backend-and-parity-triage` |
| `onednn-backend-unimplemented-primitive` | planned | discriminating | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `primitive-or-graph`, `backend-and-parity-triage` |
| `onednn-benchdnn-no-ref-memory` | implemented | smoke | ceiling | executable | hosted-cpu | live | maintainer-incident | reproduce -> investigate -> repair -> verify | generic-cpu | `backend-and-parity-triage`, `benchdnn-and-reorders` |

## uxl-onemath (oneMath)

### Capabilities

- `math-contracts` (correctness): Preserve layout, precision, dimensions, strides, seeds, and event dependencies.
- `domain-and-dispatch` (selection): Choose the domain, runtime or compile-time dispatch, and host or device API.
- `backend-build-and-link` (integration): Configure backend wrappers, CMake targets, vendor libraries, and loader paths.
- `runtime-backend-triage` (debugging): Separate link success, runtime dispatch, device discovery, and backend availability.
- `representative-math-validation` (performance): Validate known answers before measuring representative sizes and dispatch overhead.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `onemath-runtime-library-missing` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `domain-and-dispatch`, `backend-build-and-link`, `runtime-backend-triage`, `representative-math-validation` |
| `onemath-blas-leading-dimension` | planned | discriminating | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `math-contracts`, `domain-and-dispatch` |
| `onemath-deprecated-header-include` | implemented | smoke | ceiling | executable | hosted-cpu | live | maintainer-incident | reproduce -> investigate -> repair -> verify | generic-cpu | `backend-build-and-link` |
| `onemath-rng-device-event-chain` | planned | discriminating | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `math-contracts`, `domain-and-dispatch`, `runtime-backend-triage` |
| `onemath-third-party-backend-wrapper` | planned | smoke | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `backend-build-and-link`, `runtime-backend-triage` |
| `onemath-dispatch-overhead-benchmark` | planned | smoke | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `math-contracts`, `representative-math-validation` |

## uxl-onedal (oneDAL)

### Capabilities

- `analytics-parity` (correctness): Preserve preprocessing, seeds, model outputs, metrics, and tolerances.
- `interface-and-mode` (selection): Choose sklearn extension or native API and batch, online, or distributed mode.
- `tables-and-frameworks` (integration): Integrate table orientation, dense or sparse layouts, and Python or C++ boundaries.
- `quality-regression-triage` (debugging): Diagnose changed model quality, unsupported acceleration, and conversion mistakes.
- `conversion-aware-benchmarking` (performance): Measure representative analytics workloads including data conversion costs.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `onedal-sklearn-or-native-kmeans` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `analytics-parity`, `interface-and-mode` |
| `onedal-table-orientation-regression` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `analytics-parity`, `tables-and-frameworks`, `quality-regression-triage` |
| `onedal-batch-online-distributed-choice` | implemented | smoke | ceiling | answer-quality | hosted-container | review | not-applicable | investigate | none | `analytics-parity`, `interface-and-mode` |
| `onedal-unavailable-gpu-path` | planned | discriminating | uncalibrated | executable | target-gpu | live | unassigned | reproduce -> investigate -> repair -> verify | target-gpu | `interface-and-mode`, `quality-regression-triage` |
| `onedal-conversion-cost-benchmark` | planned | smoke | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `tables-and-frameworks`, `conversion-aware-benchmarking` |
| `onedal-train-infer-metric-parity` | planned | smoke | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `analytics-parity`, `conversion-aware-benchmarking` |

## uxl-onetbb (oneTBB)

### Capabilities

- `race-order-and-exception-safety` (correctness): Preserve race freedom, ordering, determinism, cancellation, and exceptions.
- `parallel-pattern-selection` (selection): Choose loops, reductions, scans, pipelines, graphs, or explicit task trees.
- `runtime-composition` (integration): Compose arenas, global limits, foreign thread pools, containers, and allocators.
- `scheduler-triage` (debugging): Diagnose oversubscription, blocking work, starvation, races, and scheduler behavior.
- `grain-affinity-benchmarking` (performance): Benchmark realistic core counts, grainsize, affinity, and scheduling overhead.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `onetbb-histogram-local-aggregation` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `race-order-and-exception-safety`, `parallel-pattern-selection` |
| `onetbb-stable-compaction-scan` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `race-order-and-exception-safety`, `parallel-pattern-selection` |
| `onetbb-bounded-image-flow-graph` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `parallel-pattern-selection`, `scheduler-triage` |
| `onetbb-nested-thread-pool-arena` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `runtime-composition`, `scheduler-triage`, `grain-affinity-benchmarking` |
| `onetbb-cancellation-exception-propagation` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `race-order-and-exception-safety`, `runtime-composition` |
| `onetbb-grainsize-affinity-regression` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `scheduler-triage`, `grain-affinity-benchmarking` |
| `onetbb-join-node-ordering` | implemented | smoke | ceiling | executable | hosted-cpu | live | maintainer-incident | reproduce -> investigate -> repair -> verify | generic-cpu | `race-order-and-exception-safety`, `parallel-pattern-selection`, `scheduler-triage` |

## uxl-onedpl (oneDPL)

### Capabilities

- `algorithm-contracts` (correctness): Preserve serial semantics, stability, ordering, lifetime, and synchronization.
- `execution-policy-choice` (selection): Choose host or device policies from data location, device, and workload.
- `queue-data-and-iterators` (integration): Integrate owned queues, USM or buffers, iterator categories, and device lambdas.
- `device-result-triage` (debugging): Diagnose synchronization, unsupported iterators, backend, and data-access failures.
- `transfer-aware-benchmarking` (performance): Measure transfers, launch, synchronization, and representative range sizes.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `onedpl-host-or-device-sort` | planned | discriminating | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `algorithm-contracts`, `execution-policy-choice` |
| `onedpl-missing-device-synchronization` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `algorithm-contracts`, `queue-data-and-iterators`, `device-result-triage` |
| `onedpl-iterator-category-failure` | planned | discriminating | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `queue-data-and-iterators`, `device-result-triage` |
| `onedpl-stable-ordering-contract` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `algorithm-contracts`, `execution-policy-choice` |
| `onedpl-host-backend-configuration` | planned | smoke | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `execution-policy-choice`, `queue-data-and-iterators` |
| `onedpl-transfer-inclusive-benchmark` | planned | smoke | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `algorithm-contracts`, `transfer-aware-benchmarking` |

## uxl-oneccl (oneCCL)

### Capabilities

- `collective-contracts` (correctness): Preserve rank symmetry, sequence, buffers, counts, datatypes, roots, and waits.
- `api-and-collective-choice` (selection): Choose the API surface and collective matching the communication semantics.
- `launcher-plugin-framework` (integration): Integrate launchers, communicators, plugins, devices, and framework wrappers.
- `distributed-hang-triage` (debugging): Use per-rank evidence to diagnose divergent calls, visibility, and completion hangs.
- `topology-worker-benchmarking` (performance): Measure rank count, topology, tensor size, transport, workers, and affinity.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `oneccl-async-allreduce-wait` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `collective-contracts`, `api-and-collective-choice` |
| `oneccl-divergent-collective-sequence` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `collective-contracts`, `distributed-hang-triage` |
| `oneccl-datatype-count-mismatch` | implemented | smoke | no-lift | answer-quality | hosted-container | fixture | constructed | investigate | none | `collective-contracts`, `distributed-hang-triage` |
| `oneccl-cpp-or-nccl-like-api` | planned | smoke | uncalibrated | answer-quality | hosted-container | review | not-applicable | investigate | none | `api-and-collective-choice`, `launcher-plugin-framework` |
| `oneccl-plugin-rank-visibility` | planned | discriminating | uncalibrated | executable | target-distributed | live | unassigned | reproduce -> investigate -> repair -> verify | target-distributed | `launcher-plugin-framework`, `distributed-hang-triage` |
| `oneccl-worker-affinity-regression` | planned | smoke | uncalibrated | executable | target-distributed | live | unassigned | reproduce -> investigate -> repair -> verify | target-distributed | `launcher-plugin-framework`, `topology-worker-benchmarking` |

## uxl-sycl-build-debug (UXL cross-project)

### Capabilities

- `reproducible-smoke-contract` (correctness): Preserve the original failure and verify build plus runtime with a minimal smoke test.
- `failure-phase-classification` (selection): Classify configure, compile, link, load, or device-selection failures before acting.
- `toolchain-package-runtime` (integration): Integrate compiler, CMake cache, package roots, target flags, loaders, and drivers.
- `evidence-driven-triage` (debugging): Use exact commands, probe output, loader evidence, and one-variable changes.
- `build-runtime-cost-boundaries` (performance): Avoid performance claims until the intended device and runtime path are proven.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sycl-device-discovery` | implemented | hardware | manual | hardware | manual-gpu | live | not-applicable | reproduce -> verify | target-gpu | `reproducible-smoke-contract`, `failure-phase-classification`, `toolchain-package-runtime`, `evidence-driven-triage` |
| `sycl-cmake-compiler-cache` | implemented | discriminating | headroom | answer-quality | hosted-container | fixture | constructed | investigate | none | `failure-phase-classification`, `toolchain-package-runtime`, `evidence-driven-triage` |
| `sycl-compile-time-backend-link` | planned | discriminating | uncalibrated | executable | hosted-cpu | live | unassigned | reproduce -> investigate -> repair -> verify | generic-cpu | `reproducible-smoke-contract`, `failure-phase-classification`, `toolchain-package-runtime` |
| `sycl-loader-plugin-mismatch` | implemented | smoke | no-lift | answer-quality | hosted-container | fixture | constructed | investigate | none | `failure-phase-classification`, `toolchain-package-runtime`, `evidence-driven-triage` |
| `sycl-selector-silent-cpu-fallback` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `reproducible-smoke-contract`, `evidence-driven-triage`, `build-runtime-cost-boundaries` |
| `sycl-reproducible-environment-report` | planned | smoke | uncalibrated | hardware | target-device | live | not-applicable | reproduce -> verify | target-device | `reproducible-smoke-contract`, `toolchain-package-runtime`, `build-runtime-cost-boundaries` |

## uxl-performance-validation (UXL cross-project)

### Capabilities

- `correctness-gated-measurement` (correctness): Define references, tolerances, ordering, limits, and failure behavior before timing.
- `benchmark-scope-selection` (selection): Choose representative sizes, baselines, boundaries, iterations, and claims.
- `library-and-hardware-context` (integration): Integrate library-specific hooks, data movement, async events, topology, and hardware.
- `invalid-claim-triage` (debugging): Detect missing synchronization, biased baselines, numerical errors, and environmental noise.
- `repeatable-performance-evidence` (performance): Measure warmup, steady state, variance, bottlenecks, and bounded speedup claims.

### Task portfolio

| Task | Status | Role | Calibration | Track | Environment | Reproduction | Origin | Workflow | Hardware | Covers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `performance-tiny-async-gpu-claim` | implemented | smoke | no-lift | answer-quality | hosted-container | fixture | constructed | investigate | none | `correctness-gated-measurement`, `benchmark-scope-selection`, `invalid-claim-triage` |
| `performance-benchmark-report-repair` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `benchmark-scope-selection`, `repeatable-performance-evidence` |
| `performance-floating-reduction-tolerance` | implemented | smoke | ceiling | executable | hosted-cpu | live | constructed | reproduce -> investigate -> repair -> verify | generic-cpu | `correctness-gated-measurement`, `invalid-claim-triage` |
| `performance-transfer-scope-comparison` | planned | discriminating | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `benchmark-scope-selection`, `library-and-hardware-context`, `repeatable-performance-evidence` |
| `performance-cgroup-concurrency-quota` | implemented | smoke | ceiling | executable | hosted-cpu | live | maintainer-incident | reproduce -> investigate -> repair -> verify | generic-cpu | `library-and-hardware-context`, `invalid-claim-triage`, `repeatable-performance-evidence` |
| `performance-profile-after-regression` | planned | discriminating | uncalibrated | executable | target-device | live | unassigned | reproduce -> investigate -> repair -> verify | target-device | `library-and-hardware-context`, `invalid-claim-triage`, `repeatable-performance-evidence` |
