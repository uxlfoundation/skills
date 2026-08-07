#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

std::vector<std::size_t> histogram(
    const std::vector<int>& values,
    std::size_t bins);

std::vector<std::size_t> reference(
    const std::vector<int>& values,
    std::size_t bins) {
    std::vector<std::size_t> counts(bins, 0);
    for (const int value : values) {
        ++counts[static_cast<std::size_t>(value) % bins];
    }
    return counts;
}

int main() {
    std::mt19937 generator(42);
    std::uniform_int_distribution<int> distribution(0, 1000000);
    std::vector<int> random_values(250000);
    std::generate(random_values.begin(), random_values.end(), [&] {
        return distribution(generator);
    });

    const std::vector<std::vector<int>> datasets = {
        {},
        {0, 1, 2, 3, 3, 7, 15, 31},
        std::vector<int>(10000, 5),
        random_values,
    };
    for (const std::size_t bins : {1U, 2U, 8U, 16U, 31U}) {
        for (const auto& values : datasets) {
            for (int repetition = 0; repetition != 4; ++repetition) {
                if (histogram(values, bins) != reference(values, bins)) {
                    throw std::runtime_error("histogram result mismatch");
                }
            }
        }
    }
    std::cout << "oneTBB histogram verifier passed\n";
}
