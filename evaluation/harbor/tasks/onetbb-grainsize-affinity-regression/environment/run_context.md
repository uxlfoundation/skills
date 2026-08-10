# Regression context

- The old host has two 16-core NUMA nodes with SMT disabled. Production previously used CPUs 0-15 and initialized both stencil buffers on node 0.
- The new container CPU set is 0-7,16-23. Its loader still first-touches the buffers on node 0. Production did not record the effective CPU set, NUMA memory placement, worker count, compiler flags, or oneTBB version beside each result.
- A preceding refactor replaced an expensive nonlinear transform with the inexpensive three-point expression in `current_loop.cpp`; the explicit range and partitioner were retained.
- `medium,high` is a controlled build that restores representative arithmetic without changing indexing or memory traffic. It is not the production body.
- `node0-local` and `split-numa` are controlled placements of the same binary. `split-numa` allows eight cores from each NUMA node while the buffers remain first-touched on node 0.
- Every table time surrounds the completed function call, not task submission. Each row includes five warmups and 30 recorded calls. `median_ms` and `p95_ms` summarize those calls.
- `same-buffers` repeats the same index-to-buffer mapping. `new-buffer-each-call` allocates and initializes a replacement buffer before every recorded call; allocation time is outside the table time.
- `affinity-g256` and `affinity-g4096` retain the same `oneapi::tbb::affinity_partitioner` object across the recorded calls for that row.
- `body_calls_per_step` counts loop-body invocations, not operating-system threads. Checksums were compared with the same serial stencil after every variant.
