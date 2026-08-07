#include <algorithm>
#include <cstddef>
#include <iostream>
#include <iterator>
#include <random>
#include <stdexcept>
#include <vector>

#include <oneapi/tbb/global_control.h>

std::vector<int> stable_compact(const std::vector<int>& values);

std::vector<int> reference(const std::vector<int>& values) {
    std::vector<int> output;
    output.reserve(values.size());
    std::copy_if(values.begin(), values.end(), std::back_inserter(output), [](int value) {
        return value >= 0;
    });
    return output;
}

void check(const std::vector<int>& values) {
    const auto expected = reference(values);
    const auto original = values;
    for (const std::size_t limit : {1U, 2U, 4U}) {
        oneapi::tbb::global_control control(
            oneapi::tbb::global_control::max_allowed_parallelism, limit);
        for (int repetition = 0; repetition != 6; ++repetition) {
            if (stable_compact(values) != expected) {
                throw std::runtime_error("stable compaction result mismatch");
            }
            if (values != original) {
                throw std::runtime_error("stable compaction modified its input");
            }
        }
    }
}

int main() {
    check({});
    check({-9, -8, -7});
    check({0, 1, 2, 3});
    check({5, -1, 5, -2, 4, 0, -3, 4});
    check({-1, 8, -2, 7, -3, 6, -4, 5, -5, 4});

    std::mt19937 generator(42);
    std::uniform_int_distribution<int> distribution(-1000000, 1000000);
    std::vector<int> random_values(250000);
    std::generate(random_values.begin(), random_values.end(), [&] {
        return distribution(generator);
    });
    check(random_values);

    std::cout << "oneTBB stable compaction verifier passed\n";
}
