#include <oneapi/dpl/execution>
#include <oneapi/dpl/numeric>

#include <cstdint>
#include <forward_list>
#include <iostream>
#include <numeric>
#include <vector>

struct move_only_value {
    std::int64_t value;

    move_only_value(std::int64_t v) : value(v) {}
    move_only_value(const move_only_value&) = delete;
    move_only_value& operator=(const move_only_value&) = delete;
    move_only_value(move_only_value&&) noexcept = default;
    move_only_value& operator=(move_only_value&&) noexcept = default;
};

struct add_values {
    move_only_value operator()(const move_only_value& left, const move_only_value& right) const {
        return move_only_value{left.value + right.value};
    }
};

struct lift_value {
    move_only_value operator()(int value) const { return move_only_value{value}; }
};

struct multiply_values {
    move_only_value operator()(int left, int right) const {
        return move_only_value{std::int64_t(left) * right};
    }
};

static bool check(const char* name, std::int64_t actual, std::int64_t expected) {
    std::cout << name << '=' << actual << " expected=" << expected << '\n';
    return actual == expected;
}

int main() {
    std::vector<int> values(8191);
    std::iota(values.begin(), values.end(), -4000);
    const auto expected_sum = std::accumulate(values.begin(), values.end(), std::int64_t{37});

    auto par_reduce = std::reduce(oneapi::dpl::execution::par,
                                  values.begin(), values.end(), move_only_value{37}, add_values{});
    auto unseq_reduce = std::reduce(oneapi::dpl::execution::par_unseq,
                                    values.begin(), values.end(), move_only_value{37}, add_values{});

    std::vector<int> factors(values.size());
    for (std::size_t i = 0; i < factors.size(); ++i) factors[i] = int(i % 5) - 2;
    std::int64_t expected_product_sum = 19;
    for (std::size_t i = 0; i < values.size(); ++i) expected_product_sum += std::int64_t(values[i]) * factors[i];
    auto binary = std::transform_reduce(oneapi::dpl::execution::par,
                                        values.begin(), values.end(), factors.begin(),
                                        move_only_value{19}, add_values{}, multiply_values{});

    std::forward_list<int> forward_values(values.begin(), values.begin() + 257);
    const auto expected_forward = std::accumulate(forward_values.begin(), forward_values.end(), std::int64_t{-11});
    auto forward = std::transform_reduce(oneapi::dpl::execution::par,
                                         forward_values.begin(), forward_values.end(),
                                         move_only_value{-11}, add_values{}, lift_value{});

    auto empty = std::transform_reduce(oneapi::dpl::execution::par,
                                       values.begin(), values.begin(),
                                       move_only_value{1234567}, add_values{}, lift_value{});

    bool ok = true;
    ok &= check("par_reduce", par_reduce.value, expected_sum);
    ok &= check("par_unseq_reduce", unseq_reduce.value, expected_sum);
    ok &= check("binary_transform_reduce", binary.value, expected_product_sum);
    ok &= check("forward_transform_reduce", forward.value, expected_forward);
    ok &= check("empty_transform_reduce", empty.value, 1234567);
    return ok ? 0 : 1;
}
