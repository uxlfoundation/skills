#include <atomic>
#include <cstddef>
#include <vector>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/parallel_for.h>

std::vector<int> stable_compact(const std::vector<int>& values) {
    std::vector<int> output(values.size());
    std::atomic<std::size_t> next{0};

    oneapi::tbb::parallel_for(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size()),
        [&](const oneapi::tbb::blocked_range<std::size_t>& range) {
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                if (values[index] >= 0) {
                    output[next.fetch_add(1, std::memory_order_relaxed)] = values[index];
                }
            }
        });

    output.resize(next.load(std::memory_order_relaxed));
    return output;
}
