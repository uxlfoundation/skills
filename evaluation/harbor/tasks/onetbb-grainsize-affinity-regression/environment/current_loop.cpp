#include <cstddef>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/parallel_for.h>
#include <oneapi/tbb/partitioner.h>

void stencil_pass(
    const float* input,
    float* output,
    std::size_t elements) {
    output[0] = input[0];
    output[elements - 1] = input[elements - 1];

    oneapi::tbb::parallel_for(
        oneapi::tbb::blocked_range<std::size_t>(1, elements - 1, 1),
        [&](const oneapi::tbb::blocked_range<std::size_t>& range) {
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                output[index] =
                    0.25F * input[index - 1] +
                    0.50F * input[index] +
                    0.25F * input[index + 1];
            }
        },
        oneapi::tbb::simple_partitioner{});
}
