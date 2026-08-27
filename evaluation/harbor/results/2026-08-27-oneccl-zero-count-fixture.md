# oneCCL zero-count topology fixture: 2026-08-27

## Outcome

`oneccl-zero-count-topo-alltoallv` is an executable, maintainer-incident-derived source fixture for [oneCCL issue #174](https://github.com/uxlfoundation/oneCCL/issues/174). The pinned baseline scores 0 because it retains one-past pointers for zero-count peers. Applying the oracle repair makes the public reproducer and hidden boundary cases score 1.

## What it checks

- The original 4,096-float live segment followed by a zero-count peer.
- Leading, middle, trailing, and all-zero peer layouts.
- Send and receive slice boundaries with non-unit datatype sizes.
- In-place temporary segments.
- Preservation of nonzero offsets, counts, datatypes, and the topology algorithm.

The repair follows upstream commit [`993878af`](https://github.com/uxlfoundation/oneCCL/commit/993878af0301b2cd8c9c1e56a45d1d5273938b0d), released in [oneCCL 2021.17](https://github.com/uxlfoundation/oneCCL/releases/tag/2021.17).

## Evidence boundary

The task runs on a generic hosted CPU and validates the source repair contract. It does not reproduce the original Aurora Level Zero driver failure. GLOW's discrete Arc B580 plus integrated A780 topology could not produce an unconfounded affected-versus-fixed comparison, so live hardware coverage remains open.

Local container calibration on evaluator revision pending commit:

- Baseline: reward 0; both public and hidden tests reject non-null zero-count slices.
- Oracle: reward 1; public and hidden tests pass.

The Harbor 0.20.0 oracle job `harbor-jobs/uxl-oneccl-zero-count-oracle` completed 1/1 trial at reward 1 with zero exceptions on GLOW through WSL and Docker Desktop. Its `result.json` SHA-256 is `B3224A63FAEC5BC0EC1A9F5C4059FCB9113577111561128EA7F079AABB019B96`.

The final evaluator revision will be added after the tracked task is committed.
