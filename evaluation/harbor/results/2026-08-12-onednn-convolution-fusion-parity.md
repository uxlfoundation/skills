# oneDNN convolution-fusion parity evaluation

Date: 2026-08-12

## Purpose

Add real hosted-CPU oneDNN coverage for a fused residual block whose observable contract is `ReLU(convolution + bias + residual)`. The constructed integration has two coupled errors: it applies ReLU before the sum post-op, and it initializes the plain destination with zeros before reordering into the primitive-selected destination layout instead of preserving the residual.

## Runtime and source basis

- Debian bookworm `libdnnl-dev` and `libdnnl2` version `2.6.3-1`.
- Generic CPU with `ONEDNN_MAX_CPU_ISA=AVX2`; no target-device or performance claim.
- Actual oneDNN `convolution_forward`, `format_tag::any` descriptors, reorder operations, and fused sum plus eltwise post-ops.
- The official [post-ops guide](https://uxlfoundation.github.io/oneDNN/dev_guide_attributes_post_ops.html) defines ordered post-op execution and the sum post-op's use of existing destination data. The official [convolution example](https://uxlfoundation.github.io/oneDNN/page_convolution_example_cpp.html) demonstrates descriptor-selected layouts and destination reorder handling.

This is a constructed regression, not a maintainer incident.

## Acceptance evidence

- Unchanged reproducer: compiles and executes oneDNN, then fails with maximum absolute error `0.86538463`.
- Accepted repair: initializes the user destination from the residual, reorders it into `conv_pd.dst_desc()`, and orders sum before ReLU.
- Public repaired error: `1.7e-7`.
- Held-out verification: four unseen channel/shape/seed/residual-scale cases, including negative residual scale.
- Worst held-out maximum absolute error: `3.7117067197556253e-7`.
- Harbor `0.20.0` oracle job: `harbor-jobs/onednn-fusion-oracle-20260812`.
- Trials: 1 completed, 0 exceptions, reward `1.0`.

## Interpretation and limit

The task exercises reproduce, investigate, repair, and verify with real oneDNN on a free hosted CPU. It does not establish current-version behavior, a historical project regression, device support, or performance. A matched [three-arm calibration](2026-08-12-onednn-convolution-fusion-calibration.md) found a one-attempt quality ceiling, so the task is retained as smoke coverage rather than evidence of skill discrimination.
