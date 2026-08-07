#include <cstddef>
#include <functional>
#include <vector>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/parallel_for.h>
#include <oneapi/tbb/parallel_scan.h>

std::vector<int> stable_compact(const std::vector<int>& values) {
    std::vector<std::size_t> offsets(values.size());
    const std::size_t selected = oneapi::tbb::parallel_scan(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size()),
        std::size_t{0},
        [&](const oneapi::tbb::blocked_range<std::size_t>& range,
            std::size_t prefix,
            bool is_final_scan) {
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                if (is_final_scan) {
                    offsets[index] = prefix;
                }
                if (values[index] >= 0) {
                    ++prefix;
                }
            }
            return prefix;
        },
        std::plus<std::size_t>{});

    std::vector<int> output(selected);
    oneapi::tbb::parallel_for(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size()),
        [&](const oneapi::tbb::blocked_range<std::size_t>& range) {
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                if (values[index] >= 0) {
                    output[offsets[index]] = values[index];
                }
            }
        });
    return output;
}
