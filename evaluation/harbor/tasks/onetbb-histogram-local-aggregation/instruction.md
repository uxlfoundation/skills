Fix the unsafe shared histogram update in `/app/histogram.cpp`.

Preserve the public `histogram(const std::vector<int>& values, std::size_t bins)` interface and deterministic results. Use a oneTBB partition-local aggregation or reduction pattern instead of shared read-modify-write updates. Run correctness checks before finishing and briefly explain the concurrency bug and validation performed.
