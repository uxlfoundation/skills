#pragma once

#include <cstddef>
#include <string>
#include <vector>

enum class FailurePoint {
    none,
    transform,
    persist,
};

struct PipelineJob {
    int id{};
    int value{};
    FailurePoint failure{FailurePoint::none};
};

struct PipelineOutcome {
    int id{};
    bool success{};
    int value{};
    std::string error;
};

struct PipelineResult {
    std::vector<PipelineOutcome> outcomes;
    std::size_t max_live_scratch{};
    std::size_t live_scratch_after{};
};

PipelineResult run_pipeline(
    const std::vector<PipelineJob>& jobs,
    std::size_t capacity);
