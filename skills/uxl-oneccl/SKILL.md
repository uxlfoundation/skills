---
name: uxl-oneccl
description: "Use for oneAPI Collective Communications Library (oneCCL) work: collective operation selection, C++ and NCCL-like C API usage, SYCL mode, PyTorch DDP or Horovod integration, rank and communicator setup, process launch, plugin selection, worker thread affinity, async wait semantics, distributed training hangs, datatype/count mismatches, and performance troubleshooting."
---

# UXL oneCCL

## Purpose

Help an agent diagnose and implement oneCCL communication safely, with special attention to launch symmetry, communicator setup, async completion, and rank-local evidence.

## First Pass

1. Identify API surface: C++ API, NCCL-like C API, PyTorch DDP, Horovod, or framework wrapper.
2. Capture rank count, nodes, devices, launcher, environment variables, plugin, transport, tensor datatype/count, and whether operations are in-place.
3. For hangs, collect per-rank logs and exact launch command before changing code.
4. Check current oneCCL docs or releases when using new C API, GPU support, or plugin behavior.

## Collective Workflow

1. Match the collective to the semantic need: allreduce, allgather, alltoall, reduce-scatter, broadcast, point-to-point, or grouped calls.
2. Verify every rank enters the same collective sequence with compatible buffers, counts, datatypes, reductions, roots, and communicators.
3. Preserve async semantics. Always wait or otherwise prove completion before consuming results.
4. Start with a minimal example and one collective before layering framework integration.
5. Tune worker count, affinity, plugin, and transport only after correctness and launch symmetry are confirmed.

## Hang Triage

1. Confirm process count and rank mapping.
2. Confirm every rank reached the same collective in the same order.
3. Confirm buffer sizes, datatypes, roots, and reductions match.
4. Confirm the required plugin and device runtime are visible to every rank.
5. Reduce to two ranks and one small tensor.
6. Add logging around collective entry, submission, and wait completion.

## Gotchas

- A single rank taking a different branch can deadlock the entire job.
- Async collectives are not complete until the request is waited or otherwise synchronized.
- Environment variables must be applied consistently across ranks.
- Plugin selection can change behavior; record `CCL_PLUGIN` and related worker settings.
- Framework wrappers can hide collectives; inspect both Python/framework and oneCCL logs.

## Output Contract

When delivering oneCCL work, include:

- API path and collective sequence.
- Rank count, launcher, plugin, and relevant environment.
- Buffer/datatype/count assumptions.
- Minimal validation command.
- Any tuning separated from correctness fixes.

## References

Read [official sources](references/official-sources.md) for current C API status, plugins, launch examples, and integration notes.
