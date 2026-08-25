# SYCL maintainer incident sourcing: wave 4

The two constructed SYCL link tasks reached a quality ceiling, so the remaining discriminating slot must use an authentic failure with uncertain evidence rather than a harder synthetic link puzzle. This screen selects [oneDNN issue #2959](https://github.com/uxlfoundation/oneDNN/issues/2959) as the next reproduction candidate, but it does not yet claim maintainer-incident coverage.

## Screening ledger

| Candidate | Why it is relevant | Decision | Next gate |
| --- | --- | --- | --- |
| [oneDNN #2959](https://github.com/uxlfoundation/oneDNN/issues/2959), CPU RNN example abort | A oneDNN 3.6.1 binary built with the SYCL CPU runtime aborted with `munmap_chunk(): invalid pointer`. Maintainer triage identified SYCL/TBB plus application OpenMP runtime composition, observed that `ONEDNN_VERBOSE=all` can hide the failure by adding synchronization, and later requested `ldd` evidence to rule out a stale `libdnnl.so`. | **Primary, source-screened.** This tests failure-phase classification, verbose-pipeline judgment, runtime dependency inspection, and disciplined handling of competing hypotheses. | Pin the reported oneDNN revision and compiler/runtime, run the original example repeatedly with and without verbose mode on generic CPU, inspect the loaded library, and prove a coherent repair. Do not promote if the abort is hardware- or timing-specific. |
| [intel/llvm #16903](https://github.com/intel/llvm/issues/16903), glibc 2.41 compile failure | A minimal SYCL include failed on x86 with an older compiler after glibc 2.41 introduced an unsupported complex-float mode; the incident was fixed in glibc. | **Fallback smoke only.** It is hardware-agnostic and reproducible with a pinned OS/compiler pair, but the first diagnostic is explicit and it primarily measures version compatibility rather than UXL library use. | Use only if a small compatibility fixture is useful; do not count it as the discriminating slot without calibration evidence. |
| [intel/llvm #21972](https://github.com/intel/llvm/issues/21972), persistent-cache crash from a dynamic SYCL library | The confirmed runtime crash depends on dynamically loaded SYCL kernels and persistent-cache image sorting. The public reproduction uses llama.cpp on an Intel Arc Pro B70. | **Hardware-gated, not selected.** The issue may eventually support a CPU-minimized reproducer, but the current evidence does not justify adding target GPU infrastructure for this evaluator. | Reconsider only if maintainers provide a small backend-independent reproducer or identify the target-specific path as important skill knowledge. |
| [oneDAL #3522](https://github.com/uxlfoundation/oneDAL/issues/3522) and [#3520](https://github.com/uxlfoundation/oneDAL/issues/3520), Bazel toolchain/linkage trackers | These describe desired ICX/DPC++ feature modeling and MKL linkage policy, but they were consolidated as planning items and provide no pinned failing revision plus accepted repair boundary. | **Reject as incident evidence.** | None unless a concrete regression and repair are linked later. |

## Proposed reproduction contract

The candidate must remain a real oneDNN CPU execution task:

1. Pin oneDNN v3.6.1 commit `e72f65d70e36f552f902d35614aef7aa54f3c796` and the reported compiler/runtime family.
2. Build the original CPU RNN example with `DNNL_CPU_RUNTIME=SYCL` and preserve the external OpenMP usage that triggered the report.
3. Run enough repetitions without verbose mode to establish a stable abort rate, then repeat with `ONEDNN_VERBOSE=all` and record whether diagnostics perturb behavior.
4. Capture `ldd`, oneDNN verbose headers, compiler and runtime versions, and the exact executable/library paths before choosing a cause.
5. Verify a coherent runtime composition: either an OpenMP oneDNN CPU runtime for the OpenMP example, or a SYCL/TBB CPU runtime with an example that does not add OpenMP. Confirm the repaired binary loads the intended `libdnnl.so` and produces correct results.

The verifier must reject merely setting verbose mode, suppressing the abort, changing the workload, or asserting a stale library without loader evidence. If the original failure does not reproduce on the hosted generic CPU, this candidate remains research evidence and the portfolio must source another incident rather than simulate the crash.

## Portfolio decision

Rename the planned slot to `sycl-onednn-threading-runtime-composition`, but retain `origin: unassigned` and `calibration: uncalibrated` until the live baseline and repaired oracle both pass. The current storage-constrained workstation cannot perform the oneDNN source build until Docker's VHD is physically compacted or the reproduction is moved to a hosted runner.
