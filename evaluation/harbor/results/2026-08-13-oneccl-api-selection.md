# oneCCL C++ versus NCCL-like C API selection: 2026-08-13

## Purpose

This wave implements `oneccl-cpp-or-nccl-like-api`, a structured review task for a mixed integration: an established C++ oneCCL service, a new pure-C plugin boundary, and C calls copied from a newer repository revision than the deployed oneCCL package.

The task replaces the corresponding planned placeholder and raises the portfolio to 33 of 49 implemented tasks. oneCCL now has four of six tasks implemented.

## Evaluation contract

The answer must:

- Retain the proven C++ API for the existing C++ service rather than rewriting it for familiar names.
- Treat the NCCL-like C API as a version-gated interoperability surface, not source, binary, or behavioral NCCL compatibility.
- Bound the C path behind an adapter with one clear lifecycle owner and no mixed C/C++ handles.
- Prove support from the installed release's headers, exported symbols, loaded library, and release-matched documentation/examples.
- Distinguish compile, link, loader, and distributed collective failures.
- Preserve rank-wide collective contracts and asynchronous completion.
- Define independent two-rank C++ and, when supported, pure-C known-answer tests plus a feature-gated rollout.

The deterministic grouped rubric also rejects blanket "always use C" guidance, claims based only on repository `main`, unsafe handle mixing, missing waits, and claims of NCCL ABI compatibility.

## Harbor gate

Harbor 0.20.0 completed both control trials with zero exceptions:

| Arm | Job | Reward | Runtime |
| --- | --- | ---: | ---: |
| Reference answer | `oneccl-api-oracle-20260813-r1` | 1.000 | 23 s |
| Empty baseline | `oneccl-api-baseline-20260813-r1` | 0.000 | 15 s |

The oracle received full credit in decision, support-evidence, correctness/rollout, unsupported-claim avoidance, and answer-presence groups.

## Scope and initial decision

This is hardware-independent fixture/review evidence. It evaluates API selection, release verification, interoperability boundaries, and validation planning; it does not execute oneCCL collectives and does not count as real end-to-end maintainer-incident triage. The task enters calibration as `discriminating` / `uncalibrated` so the matched model screen can determine whether the current skill improves answer quality or efficiency.
