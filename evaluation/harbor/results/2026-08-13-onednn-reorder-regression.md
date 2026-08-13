# oneDNN constant-weight reorder regression: 2026-08-13

## Outcome

`onednn-extra-reorder-regression` adds a live, hosted-CPU integration task for a common framework/oneDNN boundary: a primitive descriptor selects an optimized weight layout, but constant user weights are repacked before every inference request instead of once.

The task executes a real oneDNN convolution from Debian's pinned `libdnnl-dev` 2.6.3 package with the CPU ISA capped at AVX2. It uses oneDNN verbose execution records to count actual reorder and convolution primitives. This follows current oneDNN inference guidance to use `format_tag::any`, query the selected descriptor, and cache constant transformed weights for reuse: [oneDNN inference guide](https://uxlfoundation.github.io/oneDNN/dev_guide_inference.html).

## Reproduction and verification

The untouched program produced numerically correct results but failed the integration contract:

| Check | Baseline | Oracle repair |
| --- | ---: | ---: |
| Convolution executions for four requests | 4 | 4 |
| Constant-weight reorder executions | 4 | 1 |
| Numerical parity | Pass | Pass |
| Harbor reward | 0 | 1 |

The repair keeps the framework-owned `oihw` weights, oneDNN-selected packed descriptor, convolution primitive, and public command interface. It allocates the selected weight memory and performs the reorder once before the request loop, then reuses the transformed constant memory.

The hidden verifier runs channel counts 16, 32, and 64 with varied rectangular shapes, iteration counts, and seeds. The Harbor oracle passed all three cases with maximum absolute error `7.01e-7`, one weight reorder per process, and the requested number of convolution executions.

## Evidence boundary

This is a `constructed` live task, not a maintainer incident. It proves that an agent can repair and verify redundant oneDNN work on a generic hosted CPU. It does not claim a speedup, a current-version performance characteristic, or behavior on every backend or device. The measured fact is the removed primitive execution at unchanged correctness.

## Calibration

The matched [oneDNN reorder calibration](2026-08-13-onednn-reorder-calibration.md) reached full reward in all three arms. The task is therefore classified as `ceiling` and retained as smoke coverage rather than evidence that the current skill improves quality or token efficiency.

## Reproduction

- Oracle job: `harbor-jobs/onednn-reorder-oracle-20260813/result.json`.
- Environment: Debian Bookworm, `libdnnl-dev=2.6.3-1`, generic CPU, `ONEDNN_MAX_CPU_ISA=AVX2`.
- Public command: `bash /app/reproduce.sh`.
