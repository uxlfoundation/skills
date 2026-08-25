#include <charconv>
#include <cstddef>
#include <iostream>
#include <string_view>

extern "C" int run_sycl_transform(
    int count,
    int seed,
    long long *checksum,
    char *device_name,
    std::size_t device_name_size);

namespace {
int parse_integer(const char *text) {
    int value = 0;
    const std::string_view view(text);
    const auto result = std::from_chars(view.data(), view.data() + view.size(), value);
    if (result.ec != std::errc {} || result.ptr != view.data() + view.size()) return -1;
    return value;
}

long long expected_checksum(int count, int seed) {
    long long result = 0;
    for (int index = 0; index < count; ++index) {
        result += (((index * 17 + seed) % 97) * 3 + 1);
    }
    return result;
}
}  // namespace

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "usage: sycl_probe COUNT SEED\n";
        return 2;
    }

    const int count = parse_integer(argv[1]);
    const int seed = parse_integer(argv[2]);
    if (count <= 0 || seed < 0) return 2;

    long long checksum = 0;
    char device_name[256] {};
    if (run_sycl_transform(count, seed, &checksum, device_name, sizeof(device_name)) != 0) {
        return 3;
    }

    const long long expected = expected_checksum(count, seed);
    std::cout << "device=" << device_name << '\n'
              << "count=" << count << '\n'
              << "seed=" << seed << '\n'
              << "checksum=" << checksum << '\n'
              << "expected=" << expected << '\n'
              << "status=" << (checksum == expected ? "ok" : "mismatch") << '\n';
    return checksum == expected ? 0 : 1;
}
