# Maintainer incident sourcing: wave 1

This wave screened public issue reports and fixes from owning projects without treating a task name as evidence. A candidate is `verified` only after the original failure runs in the evaluator, the unchanged baseline fails, and an accepted repair passes the verifier. `Source-screened` candidates retain `origin: unassigned` in `suites.json` until those gates pass.

## Screening ledger

| Skill | Incident and resolution | Intended runner | State | Next gate |
| --- | --- | --- | --- | --- |
| `uxl-onednn` | [oneDNN #5732](https://github.com/uxlfoundation/oneDNN/issues/5732), fixed by [PR #5735](https://github.com/uxlfoundation/oneDNN/pull/5735) | AArch64 CPU until portability is proven | Source-screened | Run the pre-fix benchdnn command on x86-64 and AArch64; use hosted CPU only if the same assertion reproduces. |
| `uxl-onemath` | [oneMath #623](https://github.com/uxlfoundation/oneMath/issues/623), fixed by [PR #625](https://github.com/uxlfoundation/oneMath/pull/625) | Hosted CPU, compile-only | Source-screened | Pin the pre-fix headers, prove the include failure, and judge whether the task has enough diagnostic headroom to retain. |
| `uxl-onedal` | [oneDAL #1002](https://github.com/uxlfoundation/oneDAL/issues/1002), fixed by [PR #1018](https://github.com/uxlfoundation/oneDAL/pull/1018) | Hosted CPU | Source-screened | Build a redistributable pre-fix legacy oneDAL image and verify all prediction outputs, not only process completion. |
| `uxl-onetbb` | [oneTBB #1969](https://github.com/uxlfoundation/oneTBB/issues/1969), resolved by maintainer guidance | Hosted CPU | **Verified and implemented** | Calibrate no-skill, previous-skill, and candidate-skill arms for `onetbb-join-node-ordering`. |
| `uxl-onedpl` | [oneDPL #2296](https://github.com/uxlfoundation/oneDPL/issues/2296), fixed by [PR #2371](https://github.com/uxlfoundation/oneDPL/pull/2371) | Hosted CPU if the host backend reproduces | Source-screened | Pin the pre-fix tree and prove the reverse-iterator compile failure with the smallest open toolchain. |
| `uxl-oneccl` | [oneCCL #174](https://github.com/uxlfoundation/oneCCL/issues/174), confirmed fixed in oneCCL 2021.17 | Aurora-class distributed Intel GPU | Hardware-gated | Do not emulate the Level Zero address-range failure. Obtain matching hardware only if this incident is selected for durable coverage. |
| `uxl-sycl-build-debug` | [intel/llvm #5071](https://github.com/intel/llvm/issues/5071), resolved in later compiler releases | Hosted CPU, link-only | Source-screened | Pin an affected compiler and confirm the undefined reference occurs before device execution. |
| `uxl-performance-validation` | [oneTBB #1760](https://github.com/uxlfoundation/oneTBB/issues/1760), fixed by [PR #1777](https://github.com/uxlfoundation/oneTBB/pull/1777) | Hosted CPU container with cgroup quota | Source-screened | Prove the host exposes more CPUs than the container quota and define a non-flaky concurrency/performance verifier. |

## Implemented task

`onetbb-join-node-ordering` adapts the public oneTBB incident into a multi-worker flow graph. The untouched reproducer cross-pairs unrelated tokens because it assumes FIFO delivery across parallel graph work. The task accepts either of the maintainer-supported graph-level repairs: restore order with a `sequencer_node`, or correlate inputs with a `key_matching` join.

| Check | Result |
| --- | ---: |
| Original public reproducer | 77 mismatches across 20 runs |
| Hardened evaluator baseline | Reward 0 in 10 of 10 runs |
| Live baseline failure | `unrelated tokens were joined` |
| Oracle repair | Reward 1 |
| Required hardware | Generic hosted CPU |

The portfolio now has 21 implemented tasks. This is the first task that is implemented, reproduces live, exercises reproduce/investigate/repair/verify, and has a verified maintainer-incident origin. All other candidate rows above remain sourcing leads, not claimed real-world coverage.

## Selection decision

The next implementation target is oneDPL #2296 if its host-backend failure can be reproduced with a portable toolchain. It is more diagnostically useful than the one-line oneMath header fix and does not inherently require target hardware. If the toolchain pin is unsuitable for free runners, the fallback is the oneMath compile-only incident; it should be retained only if calibration shows skill-sensitive headroom.
