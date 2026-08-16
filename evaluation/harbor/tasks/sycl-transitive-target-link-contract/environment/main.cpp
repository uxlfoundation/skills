#include "pipeline.hpp"

#include <charconv>
#include <iostream>
#include <string_view>

namespace {
int parse_integer(const char *text) {
    int value = 0;
    const std::string_view view(text);
    const auto result = std::from_chars(view.data(), view.data() + view.size(), value);
    if (result.ec != std::errc {} || result.ptr != view.data() + view.size()) return -1;
    return value;
}

long long expected_checksum(int count, int seed, int scale) {
    long long raw = 0;
    for (int index = 0; index < count; ++index) raw += (index * 13 + seed) % 101;
    return raw * scale + static_cast<long long>(count) * 3;
}
}  // namespace

int main(int argc, char **argv) {
    if (argc != 4) {
        std::cerr << "usage: transitive_probe COUNT SEED SCALE\n";
        return 2;
    }

    const int count = parse_integer(argv[1]);
    const int seed = parse_integer(argv[2]);
    const int scale = parse_integer(argv[3]);
    if (count <= 0 || seed < 0 || scale <= 0) return 2;

    long long checksum = 0;
    char device_name[256] {};
    if (run_transform_pipeline(
            count, seed, scale, &checksum, device_name, sizeof(device_name)) != 0) {
        return 3;
    }

    const long long expected = expected_checksum(count, seed, scale);
    std::cout << "device=" << device_name << '\n'
              << "count=" << count << '\n'
              << "seed=" << seed << '\n'
              << "scale=" << scale << '\n'
              << "checksum=" << checksum << '\n'
              << "expected=" << expected << '\n'
              << "status=" << (checksum == expected ? "ok" : "mismatch") << '\n';
    return checksum == expected ? 0 : 1;
}
