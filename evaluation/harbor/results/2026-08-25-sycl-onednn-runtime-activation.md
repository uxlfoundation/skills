# SYCL/oneDNN Runtime-Composition Task Activation

Date: 2026-08-25

## Decision

Activate `sycl-onednn-threading-runtime-composition` as an implemented, live, maintainer-incident evaluator task. It remains uncalibrated until with-skill and without-skill agent runs are retained.

## Live reproduction on GLOW

- oneDNN: v3.6.1, commit `e72f65d70e36f552f902d35614aef7aa54f3c796`
- Toolchain: Intel oneAPI 2026.1.0 DPC++/C++ compiler image, pinned by digest in the task Dockerfile
- Failing composition: oneDNN CPU runtime SYCL/TBB; application compiled with SYCL and OpenMP
- Loader evidence: local pinned `libdnnl.so.3`, `libtbb`, `libiomp5`, and `libsycl`
- Result without verbose logging: 18 failures in 20 launches, including invalid-pointer aborts and segmentation faults
- Diagnostic perturbation: zero failures in 20 launches with oneDNN verbose logging enabled; this is explicitly not accepted as a repair
- Coherent repair: oneDNN CPU runtime OpenMP; application compiled with OpenMP
- Repaired loader evidence: local pinned OpenMP `libdnnl.so.3` and `libiomp5`, with no TBB/SYCL dependency
- Repaired result: zero failures in 20 launches

## Packaged task verification

- The reduced, pinned task image retained the incident with the generic SYCL GPU-runtime build required by oneDNN's SYCL CPU runtime.
- Baseline under a four-CPU/seven-GB container limit: 12 failures in 12 launches; loader evidence resolved the pinned local SYCL oneDNN build, TBB, OpenMP, and SYCL.
- Oracle: 20 successful launches in 20 attempts; loader evidence resolved the pinned local OpenMP oneDNN build and `libiomp5`, without TBB or SYCL.
- Harbor 0.20.0: one completed oracle trial, zero exceptions, reward 1.0.
- The initial standard 35-task local smoke produced 31 reward-1.0 trials; four pre-existing images could not trust the machine's HTTPS-inspection root. After the public root was supplied through the optional container-build trust path, the unchanged 35-task oracle set produced 35 reward-1.0 trials with zero errors. See `2026-08-26-glow-container-trust.md`.

The task is CPU-only and makes no claim about current oneDNN releases, GPU behavior, or performance. Its source is [oneDNN issue 2959](https://github.com/uxlfoundation/oneDNN/issues/2959), including [maintainer guidance to use a consistent CPU runtime](https://github.com/uxlfoundation/oneDNN/issues/2959#issuecomment-2756505490).
