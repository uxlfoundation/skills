#include "runtime_composition.h"

#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

long long reference(const std::vector<int>& values) {
    long long total = 0;
    for (const int item : values) {
        const long long value = item;
        total += value * value;
    }
    return total;
}

void verify_case(
    const std::vector<std::vector<int>>& batches,
    std::size_t caller_threads,
    int concurrency_budget) {
    const auto original = batches;
    const CompositionResult result =
        run_composed(batches, caller_threads, concurrency_budget);

    require(batches == original, "input batches were modified");
    require(result.totals.size() == batches.size(), "output count mismatch");
    for (std::size_t index = 0; index != batches.size(); ++index) {
        require(result.totals[index] == reference(batches[index]), "sum-of-squares mismatch");
    }
    require(result.caller_threads_started == caller_threads, "caller pool was reduced");
    require(result.arena_concurrency == concurrency_budget, "reported arena limit mismatch");
    require(
        result.peak_compute_bodies <= static_cast<std::size_t>(concurrency_budget),
        "process-wide compute budget exceeded");
    const bool has_values = std::any_of(
        batches.begin(), batches.end(), [](const auto& batch) { return !batch.empty(); });
    if (has_values) {
        require(result.peak_compute_bodies >= 1, "no compute body was observed");
    }
    if (batches.size() >= 16 && concurrency_budget >= 2) {
        require(result.peak_compute_bodies >= 2, "computation was globally serialized");
        require(result.distinct_compute_threads >= 2, "only one compute thread was used");
    }
}

}  // namespace

int main() {
    verify_case({{}}, 1, 1);
    verify_case({{1, -2, 3, -4}}, 3, 2);

    std::mt19937 generator(20260810);
    std::uniform_int_distribution<int> distribution(-1000, 1000);
    std::vector<std::vector<int>> batches(36, std::vector<int>(4096));
    for (auto& batch : batches) {
        std::generate(batch.begin(), batch.end(), [&] { return distribution(generator); });
    }
    for (const int budget : {2, 3}) {
        verify_case(batches, 7, budget);
        verify_case(batches, 7, budget);
    }

    bool rejected_zero_callers = false;
    try {
        (void)run_composed(batches, 0, 2);
    } catch (const std::invalid_argument&) {
        rejected_zero_callers = true;
    }
    require(rejected_zero_callers, "zero caller threads were not rejected");

    bool rejected_zero_budget = false;
    try {
        (void)run_composed(batches, 2, 0);
    } catch (const std::invalid_argument&) {
        rejected_zero_budget = true;
    }
    require(rejected_zero_budget, "zero concurrency budget was not rejected");

    std::cout << "oneTBB runtime composition verifier passed\n";
}
