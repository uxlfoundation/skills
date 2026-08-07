#include <cstddef>
#include <vector>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/parallel_for.h>

std::vector<std::size_t> histogram(
    const std::vector<int>& values,
    std::size_t bins) {
    std::vector<std::size_t> counts(bins, 0);
    oneapi::tbb::parallel_for(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size()),
        [&](const oneapi::tbb::blocked_range<std::size_t>& range) {
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                const auto bucket = static_cast<std::size_t>(values[index]) % bins;
                ++counts[bucket];
            }
        });
    return counts;
}
