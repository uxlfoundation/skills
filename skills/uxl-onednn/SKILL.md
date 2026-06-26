---
name: uxl-onednn
description: "Use for oneAPI Deep Neural Network Library (oneDNN) implementation and troubleshooting: primitive selection, memory descriptors and format tags, engines, streams, graph/fusion, post-ops, framework integration, backend selection, numerical parity, and benchdnn correctness or performance workflows."
---

# UXL oneDNN

## Purpose

Help an agent produce correct, measurable oneDNN work for deep learning frameworks and applications. Prefer official oneDNN docs, examples, tests, and `benchdnn` behavior over generic deep learning advice.

## First Pass

1. Identify the task: new primitive use, graph/fusion, backend work, framework integration, correctness bug, performance regression, or build issue.
2. Capture the target engine, device, data types, tensor shapes, memory layouts, threading/runtime, and whether the code is C, C++, or framework glue.
3. Read nearby project code and tests before proposing API usage. Match existing oneDNN wrapper style.
4. If the user asks about current support, versions, or "latest" behavior, check upstream docs or releases before answering.

## Implementation Workflow

1. Define the semantic contract: operation, shapes, strides, data types, attributes, expected numerics, and allowed reorder boundaries.
2. Choose the oneDNN primitive or graph path. Use primitives for explicit control and isolated operations; consider graph/fusion only after individual operation parity is clear.
3. Build memory descriptors deliberately. Use optimized layouts only where the surrounding code can tolerate reorders and blocked formats.
4. Add attributes and post-ops only after the unfused path is correct.
5. Validate with a small deterministic case, then representative real shapes.
6. Use `benchdnn` or existing project benchmarks for performance claims. Report baseline, new result, problem shape, engine, build type, and environment.

## Gotchas

- Do not treat logical tensor shape as physical layout. Reorders and blocked formats can dominate runtime.
- Do not promise a GPU or CPU backend supports a primitive without checking docs, tests, or runtime errors.
- Do not hide numerical differences. State tolerance, accumulation type, and whether comparison is bitwise or approximate.
- Avoid fusing first. Build a reference unfused path or `benchdnn` case, then fuse and re-check.
- Reorder placement is part of the design. Keep data in optimized layout across adjacent primitives when possible.

## Output Contract

When delivering oneDNN work, include:

- Chosen primitive or graph path and why.
- Engine/device, data types, tensor shapes, and memory layout assumptions.
- Correctness validation command or test case.
- Benchmark command or reason no performance claim is made.
- Known limitations and follow-up checks.

## References

Read [official sources](references/official-sources.md) when a task depends on exact API support, current releases, `benchdnn`, graph behavior, or backend limitations.
