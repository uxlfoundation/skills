#include <oneapi/tbb/parallel_for.h>
#include <oneapi/tbb/task_arena.h>

#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sched.h>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <vector>

int schedulable_cpu_count() {
    cpu_set_t mask;
    CPU_ZERO(&mask);
    if (sched_getaffinity(0, sizeof(mask), &mask) == 0) {
        const int count = CPU_COUNT(&mask);
        if (count > 0) {
            return count;
        }
    }

    const long online = sysconf(_SC_NPROCESSORS_ONLN);
    return online > 0 ? static_cast<int>(online) : 1;
}

bool parse_positive(std::string_view text, std::uint64_t& value) {
    if (text.empty()) {
        return false;
    }
    const char* begin = text.data();
    const char* end = begin + text.size();
    const auto result = std::from_chars(begin, end, value);
    return result.ec == std::errc{} && result.ptr == end && value > 0;
}

int quota_aware_concurrency(const std::string& cpu_max_path) {
    const int schedulable = schedulable_cpu_count();
    std::ifstream input(cpu_max_path);
    std::string quota_text;
    std::string period_text;
    std::string extra;
    if (!(input >> quota_text >> period_text) || (input >> extra)) {
        return schedulable;
    }
    if (quota_text == "max") {
        return schedulable;
    }

    std::uint64_t quota = 0;
    std::uint64_t period = 0;
    if (!parse_positive(quota_text, quota) || !parse_positive(period_text, period)) {
        return schedulable;
    }

    const std::uint64_t quota_workers = quota / period + (quota % period != 0);
    const std::uint64_t bounded =
        quota_workers < static_cast<std::uint64_t>(schedulable)
            ? quota_workers
            : static_cast<std::uint64_t>(schedulable);
    return static_cast<int>(bounded > 0 ? bounded : 1);
}

int main(int argc, char** argv) {
    if (argc > 2) {
        std::cerr << "usage: quota_parallel [CPU_MAX_FILE]\n";
        return 2;
    }

    const std::string cpu_max_path = argc == 2 ? argv[1] : "/sys/fs/cgroup/cpu.max";
    const int schedulable = schedulable_cpu_count();
    const int requested = quota_aware_concurrency(cpu_max_path);

    oneapi::tbb::task_arena arena(requested);
    arena.initialize();

    std::vector<std::uint64_t> values(10'000);
    arena.execute([&] {
        oneapi::tbb::parallel_for(std::size_t{0}, values.size(), [&](std::size_t index) {
            values[index] = (index % 97) + 1;
        });
    });
    const std::uint64_t checksum =
        std::accumulate(values.begin(), values.end(), std::uint64_t{0});

    std::cout << "schedulable=" << schedulable << '\n'
              << "requested=" << requested << '\n'
              << "arena=" << arena.max_concurrency() << '\n'
              << "checksum=" << checksum << '\n';
}
