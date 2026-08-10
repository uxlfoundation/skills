#include "runtime_composition.h"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <functional>
#include <mutex>
#include <set>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

#include <oneapi/tbb/blocked_range.h>
#include <oneapi/tbb/parallel_reduce.h>
#include <oneapi/tbb/task_arena.h>

namespace {

struct ComputeTracker {
    std::atomic<std::size_t> active{0};
    std::atomic<std::size_t> peak{0};
    std::mutex mutex;
    std::set<std::thread::id> threads;
};

class ComputeScope {
public:
    explicit ComputeScope(ComputeTracker& tracker) : tracker_(tracker) {
        const std::size_t current = tracker_.active.fetch_add(1) + 1;
        std::size_t observed = tracker_.peak.load();
        while (observed < current &&
               !tracker_.peak.compare_exchange_weak(observed, current)) {
        }
        std::lock_guard<std::mutex> lock(tracker_.mutex);
        tracker_.threads.insert(std::this_thread::get_id());
    }

    ~ComputeScope() {
        tracker_.active.fetch_sub(1);
    }

private:
    ComputeTracker& tracker_;
};

long long sum_squares(const std::vector<int>& values, ComputeTracker& tracker) {
    return oneapi::tbb::parallel_reduce(
        oneapi::tbb::blocked_range<std::size_t>(0, values.size(), 32),
        0LL,
        [&](const oneapi::tbb::blocked_range<std::size_t>& range, long long partial) {
            ComputeScope scope(tracker);
            std::this_thread::sleep_for(std::chrono::microseconds(250));
            for (std::size_t index = range.begin(); index != range.end(); ++index) {
                const long long value = values[index];
                partial += value * value;
            }
            return partial;
        },
        std::plus<long long>{});
}

}  // namespace

CompositionResult run_composed(
    const std::vector<std::vector<int>>& batches,
    std::size_t caller_threads,
    int concurrency_budget) {
    if (caller_threads == 0 || concurrency_budget <= 0) {
        throw std::invalid_argument("caller threads and concurrency budget must be positive");
    }

    ComputeTracker tracker;
    std::atomic<std::size_t> next_batch{0};
    std::atomic<std::size_t> callers_started{0};
    std::vector<long long> totals(batches.size());
    std::vector<std::thread> callers;
    callers.reserve(caller_threads);

    for (std::size_t caller = 0; caller != caller_threads; ++caller) {
        callers.emplace_back([&] {
            callers_started.fetch_add(1);
            oneapi::tbb::task_arena local_arena(concurrency_budget);
            for (;;) {
                const std::size_t index = next_batch.fetch_add(1);
                if (index >= batches.size()) {
                    break;
                }
                totals[index] = local_arena.execute([&] {
                    return sum_squares(batches[index], tracker);
                });
            }
        });
    }
    for (auto& caller : callers) {
        caller.join();
    }

    std::size_t distinct_threads = 0;
    {
        std::lock_guard<std::mutex> lock(tracker.mutex);
        distinct_threads = tracker.threads.size();
    }
    return CompositionResult{
        std::move(totals),
        tracker.peak.load(),
        distinct_threads,
        callers_started.load(),
        concurrency_budget};
}
