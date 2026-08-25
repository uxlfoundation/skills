#include <oneapi/dpl/execution>
#include <oneapi/dpl/numeric>

#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

struct move_only_sum {
    std::int64_t value;

    explicit move_only_sum(std::int64_t v) : value(v) {}
    move_only_sum(const move_only_sum&) = delete;
    move_only_sum& operator=(const move_only_sum&) = delete;
    move_only_sum(move_only_sum&&) noexcept = default;
    move_only_sum& operator=(move_only_sum&&) noexcept = default;
};

struct combine {
    move_only_sum operator()(const move_only_sum& left, const move_only_sum& right) const {
        return move_only_sum{left.value + right.value};
    }
};

struct lift {
    move_only_sum operator()(int value) const { return move_only_sum{value}; }
};

int main() {
    std::vector<int> values(4096);
    std::iota(values.begin(), values.end(), 1);
    const auto expected = std::int64_t(values.size()) * (values.size() + 1) / 2;

    auto parallel = std::transform_reduce(oneapi::dpl::execution::par,
                                          values.begin(), values.end(),
                                          move_only_sum{0}, combine{}, lift{});
    auto unsequenced = std::transform_reduce(oneapi::dpl::execution::par_unseq,
                                             values.begin(), values.end(),
                                             move_only_sum{0}, combine{}, lift{});

    std::cout << "parallel=" << parallel.value
              << " par_unseq=" << unsequenced.value
              << " expected=" << expected << '\n';
    return parallel.value == expected && unsequenced.value == expected ? 0 : 1;
}
