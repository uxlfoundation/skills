#pragma once

#include <cstddef>
#include <vector>

struct CompositionResult {
    std::vector<long long> totals;
    std::size_t peak_compute_bodies{};
    std::size_t distinct_compute_threads{};
    std::size_t caller_threads_started{};
    int arena_concurrency{};
};

CompositionResult run_composed(
    const std::vector<std::vector<int>>& batches,
    std::size_t caller_threads,
    int concurrency_budget);
