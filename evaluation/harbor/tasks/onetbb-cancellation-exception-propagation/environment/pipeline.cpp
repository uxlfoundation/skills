#include "pipeline.h"

#include <atomic>
#include <chrono>
#include <memory>
#include <stdexcept>
#include <thread>
#include <vector>

#include <oneapi/tbb/flow_graph.h>

namespace {

struct ScratchTracker {
    std::atomic<std::size_t> live{0};
    std::atomic<std::size_t> maximum{0};
};

struct Scratch {
    explicit Scratch(ScratchTracker& tracker, int seed)
        : tracker(tracker), words(2048, seed) {
        const std::size_t current = tracker.live.fetch_add(1) + 1;
        std::size_t observed = tracker.maximum.load();
        while (observed < current &&
               !tracker.maximum.compare_exchange_weak(observed, current)) {
        }
    }

    ~Scratch() {
        tracker.live.fetch_sub(1);
    }

    ScratchTracker& tracker;
    std::vector<int> words;
};

struct IndexedJob {
    std::size_t index{};
    PipelineJob job;
};

struct Envelope {
    std::size_t index{};
    PipelineJob job;
    std::shared_ptr<Scratch> scratch;
    PipelineOutcome outcome;
    int transformed{};
};

}  // namespace

PipelineResult run_pipeline(
    const std::vector<PipelineJob>& jobs,
    std::size_t capacity) {
    if (capacity == 0) {
        throw std::invalid_argument("capacity must be positive");
    }

    namespace flow = oneapi::tbb::flow;
    flow::graph graph;
    ScratchTracker tracker;
    std::vector<PipelineOutcome> outcomes(jobs.size());

    flow::function_node<IndexedJob, Envelope> prepare(
        graph, flow::unlimited, [&](const IndexedJob& indexed) {
            Envelope envelope;
            envelope.index = indexed.index;
            envelope.job = indexed.job;
            envelope.scratch = std::make_shared<Scratch>(tracker, indexed.job.value);
            envelope.outcome.id = indexed.job.id;
            envelope.outcome.success = true;
            envelope.transformed = indexed.job.value * 2;
            return envelope;
        });

    flow::function_node<Envelope, Envelope> transform(
        graph, flow::unlimited, [](Envelope envelope) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            if (envelope.job.failure == FailurePoint::transform) {
                throw std::runtime_error("transform");
            }
            envelope.transformed += 3;
            return envelope;
        });

    flow::function_node<Envelope, Envelope> persist(
        graph, flow::unlimited, [](Envelope envelope) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            if (envelope.job.failure == FailurePoint::persist) {
                throw std::runtime_error("persist");
            }
            envelope.outcome.value = envelope.transformed;
            return envelope;
        });

    flow::function_node<Envelope, flow::continue_msg> complete(
        graph, flow::unlimited, [&](Envelope envelope) {
            envelope.scratch.reset();
            outcomes[envelope.index] = std::move(envelope.outcome);
            return flow::continue_msg{};
        });

    flow::make_edge(prepare, transform);
    flow::make_edge(transform, persist);
    flow::make_edge(persist, complete);

    for (std::size_t index = 0; index != jobs.size(); ++index) {
        prepare.try_put(IndexedJob{index, jobs[index]});
    }
    graph.wait_for_all();

    return PipelineResult{
        std::move(outcomes), tracker.maximum.load(), tracker.live.load()};
}
