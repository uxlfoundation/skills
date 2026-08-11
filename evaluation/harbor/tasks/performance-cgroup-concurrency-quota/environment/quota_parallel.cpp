#include <oneapi/tbb/parallel_for.h>
#include <oneapi/tbb/task_arena.h>

#include <cstdint>
#include <iostream>
#include <numeric>
#include <sched.h>
#include <string>
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

int quota_aware_concurrency(const std::string&) {
    // BUG: CPU affinity and a cgroup CPU-time quota are independent controls.
    return schedulable_cpu_count();
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
