---
name: uxl-onedal
description: "Use for oneAPI Data Analytics Library (oneDAL) and scikit-learn acceleration work: choosing Extension for Scikit-learn versus native oneDAL C++ APIs, oneAPI versus DAAL interfaces, batch/online/distributed algorithms, SYCL acceleration, table layout, model training/inference workflows, metrics validation, and performance troubleshooting."
---

# UXL oneDAL

## Purpose

Help an agent choose the right oneDAL path, preserve analytics semantics, and validate accelerated results against a clear CPU or scikit-learn reference.

## First Pass

1. Determine whether the user wants to accelerate existing Python/scikit-learn code or write native oneDAL C++.
2. Identify algorithm, data shape, data type, sparse/dense representation, batch/online/distributed mode, and target device.
3. Check whether exact API and device support are current before promising a path.
4. Read existing tests and examples near the requested algorithm.

## Path Selection

- Use Extension for Scikit-learn when the user wants minimal-change acceleration of existing scikit-learn workflows.
- Use native oneDAL oneAPI C++ interfaces when the user needs direct control, C++ integration, SYCL queues, or project-level oneDAL contributions.
- Mention DAAL only when maintaining legacy code or when the repo already uses that interface.
- Use distributed mode only when the data and launch environment are genuinely distributed; do not treat it as a faster batch default.

## Implementation Workflow

1. Define the analytics contract: preprocessing, train/test split, algorithm parameters, model outputs, metrics, random seeds, and expected tolerances.
2. Map input data into the right oneDAL table representation. Treat row/column orientation and dense/sparse layout as observable behavior.
3. Choose batch, online, or distributed computation from the workload, not from assumed performance.
4. Add a small reference path and compare representative outputs.
5. Benchmark only after correctness is stable. Include data size, mode, device, thread settings, and conversion costs.

## Gotchas

- Acceleration can disappear if table conversion or Python boundary costs dominate.
- scikit-learn parity requires matching preprocessing, defaults, seeds, and metric definitions.
- Online and distributed algorithms can have different numerical behavior from batch.
- Do not assume every oneDAL algorithm has an optimized GPU path.
- Record whether model comparison is exact, tolerance-based, or metric-based.

## Output Contract

When delivering oneDAL work, include:

- API path: sklearn extension, native oneAPI C++, or DAAL maintenance.
- Algorithm, mode, and data representation.
- Reference result and comparison method.
- Benchmark scope and what conversion costs are included.
- Unsupported or unverified features.

## References

Read [official sources](references/official-sources.md) when selecting an algorithm, interface family, or current acceleration path.
