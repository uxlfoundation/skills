#include <cstddef>
#include <vector>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/enumerable_thread_specific.h>
#include <oneapi/tbb/parallel_for.h>

std::vector<std::size_t> histogram(
    const std::vector<int>& values,
    std::size_t bins) {
    oneapi::tbb::enumerable_thread_specific<std::vector<std::size_t>> local_counts(
        [bins] { return std::vector<std::size_t>(bins, 0); });

    oneapi::tbb::parallel_for(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size()),
        [&](const oneapi::tbb::blocked_range<std::size_t>& range) {
            auto& local = local_counts.local();
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                const auto bucket = static_cast<std::size_t>(values[index]) % bins;
                ++local[bucket];
            }
        });

    std::vector<std::size_t> totals(bins, 0);
    for (const auto& local : local_counts) {
        for (std::size_t bucket = 0; bucket != bins; ++bucket) {
            totals[bucket] += local[bucket];
        }
    }
    return totals;
}
