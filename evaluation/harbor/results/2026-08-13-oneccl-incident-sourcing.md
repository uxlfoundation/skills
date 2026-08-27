# oneCCL maintainer-incident sourcing: 2026-08-13

## Outcome

This wave did not promote a new oneCCL task. The strongest candidate has a genuine target-hardware requirement, while the portable candidates lack an accepted repair boundary. Constructing a CPU mock and labeling it live end-to-end triage would overstate what the evaluator proves.

## Candidate decisions

| Candidate | Evidence | Decision |
| --- | --- | --- |
| [Issue #174](https://github.com/uxlfoundation/oneCCL/issues/174), zero-count `alltoallv` | On Aurora GPUs, the topology algorithm passes a one-past-the-allocation pointer to `zeMemGetAddressRange` when a final peer count is zero. Maintainer analysis identified the boundary error, and release 2021.17 commit `993878af0301b2cd8c9c1e56a45d1d5273938b0d` guards zero-count send, receive, and temporary buffers. | Verified target-GPU candidate. Preserve for an Intel Level Zero runner; a CPU mock may supplement but cannot replace the hardware reproduction. |
| [Issue #109](https://github.com/uxlfoundation/oneCCL/issues/109), multi-worker CPU allreduce | Failure depends on the PSM3/libfabric path and large messages. The issue records alternate-provider and kernel-setting workarounds but was closed after inactivity without an accepted oneCCL repair. | Reject as maintainer-incident evaluation evidence. |
| [Issue #54](https://github.com/uxlfoundation/oneCCL/issues/54), GCC build failures | The report combines a missing standard-library include, an AVX-512 BF16 conversion, and torch-ccl/PyTorch API incompatibility. Maintainers later stated that the oneCCL build issues were fixed, but the public history does not provide a single precise accepted repair boundary for the reported combination. | Reject until a specific source/fix pair is identified. |
| [Issue #10](https://github.com/uxlfoundation/oneCCL/issues/10), resizable KVS failure | Maintainer reported the problem fixed, but the old resizable runtime scenario has no linked repair and requires reconstructing an obsolete environment. | Reject for now. |

## Why issue #174 needs target hardware

The failure is not merely arithmetic on offsets. It depends on a Level Zero device allocation, the driver's allocation granularity, IPC-handle creation, the topology `alltoallv` algorithm, and `zeMemGetAddressRange` rejecting the one-past-end device pointer. Hosted CPU execution can verify the new zero-count branch, but cannot reproduce or clear the actual driver/API failure.

This is the evaluator's hardware policy in practice: require target hardware only when the incident itself depends on it, and do not create target-specific skill guidance merely because the verification environment is target-specific.

## Next gate

oneCCL remains at zero real end-to-end tasks. The next promotion requires either:

1. Access to an Intel Level Zero GPU runner for issue #174, with the topology algorithm and zero-count neighbor pattern preserved; or
2. A maintainer-supplied CPU/provider incident with a reproducible source revision and accepted repair.

The planned hosted `oneccl-cpp-or-nccl-like-api` task can still improve API-selection coverage, but it must remain fixture/review evidence and must not be reported as real incident triage.

## 2026-08-27 GLOW activation attempt

GLOW proved that its current oneCCL 2022.1 stack can execute a four-rank, topology-selected, zero-count `alltoallv` on the Intel Arc A780 through Level Zero when the container uses pidfd IPC. This is a current-stack control, not an affected-version reproduction.

Affected oneCCL 2021.15.6 and repaired 2021.17 were then compiled with compatible 2025 toolchains. Four ranks forced onto the A780 failed in the same Level Zero memory-manager path in both revisions, so GPU oversubscription confounded the comparison. With one rank on each GLOW GPU, both revisions failed during communicator setup because GLOW pairs a discrete Arc B580 with the integrated A780. Neither comparison isolates issue #174.

The new `oneccl-zero-count-topo-alltoallv` task is therefore an executable source fixture. It preserves the incident's 4,096-float live neighbor and zero-count peer pattern and checks the accepted send, receive, and in-place temporary repair, but it is labeled `fixture` and does not close the live hardware gate.

The remaining gate is a homogeneous multi-GPU Level Zero target matching the original topology class, or maintainer-supplied evidence from such a system.
