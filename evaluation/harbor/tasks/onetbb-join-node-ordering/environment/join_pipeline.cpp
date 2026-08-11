#include "join_pipeline.h"

#include <chrono>
#include <cstdint>
#include <thread>
#include <tuple>

#include <oneapi/tbb/flow_graph.h>

std::vector<JoinedToken> run_join_pipeline(std::size_t token_count) {
    using ReceiveTuple = std::tuple<std::int32_t, std::int32_t>;
    using WorkerTuple = std::tuple<ReceiveTuple, std::int32_t>;

    oneapi::tbb::flow::graph graph;
    std::int32_t next_token = 0;
    const auto limit = static_cast<std::int32_t>(token_count);

    oneapi::tbb::flow::input_node<std::int32_t> trigger(
        graph,
        [&](oneapi::tbb::flow_control& control) {
            if (next_token == limit) {
                control.stop();
                return std::int32_t{-1};
            }
            return next_token++;
        });

    oneapi::tbb::flow::join_node<ReceiveTuple, oneapi::tbb::flow::queueing>
        receive_join(graph);
    oneapi::tbb::flow::function_node<ReceiveTuple, ReceiveTuple> receiver(
        graph,
        oneapi::tbb::flow::unlimited,
        [](const ReceiveTuple& item) {
            const auto token = std::get<0>(item);
            const auto delay = 8 - (token % 8);
            std::this_thread::sleep_for(std::chrono::microseconds(200 * delay));
            return item;
        });
    oneapi::tbb::flow::join_node<WorkerTuple, oneapi::tbb::flow::queueing>
        worker_join(graph);

    std::vector<JoinedToken> result;
    result.reserve(token_count);
    oneapi::tbb::flow::function_node<WorkerTuple, oneapi::tbb::flow::continue_msg>
        worker(
            graph,
            oneapi::tbb::flow::serial,
            [&](const WorkerTuple& item) {
                const auto& received = std::get<0>(item);
                result.push_back({std::get<0>(received), std::get<1>(item)});
                return oneapi::tbb::flow::continue_msg{};
            });

    oneapi::tbb::flow::make_edge(
        trigger, oneapi::tbb::flow::input_port<0>(receive_join));
    oneapi::tbb::flow::make_edge(receive_join, receiver);
    oneapi::tbb::flow::make_edge(
        receiver, oneapi::tbb::flow::input_port<0>(worker_join));
    oneapi::tbb::flow::make_edge(worker_join, worker);

    for (std::int32_t token = 0; token != limit; ++token) {
        oneapi::tbb::flow::input_port<1>(receive_join).try_put(token);
        oneapi::tbb::flow::input_port<1>(worker_join).try_put(token);
    }

    trigger.activate();
    graph.wait_for_all();
    return result;
}
