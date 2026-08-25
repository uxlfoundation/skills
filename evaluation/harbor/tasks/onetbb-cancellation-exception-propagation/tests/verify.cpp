#include "pipeline.h"

#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

void verify_batch(const std::vector<PipelineJob>& jobs, std::size_t capacity) {
    const auto original = jobs;
    const PipelineResult result = run_pipeline(jobs, capacity);

    require(jobs.size() == original.size(), "input size changed");
    for (std::size_t index = 0; index != jobs.size(); ++index) {
        require(jobs[index].id == original[index].id, "input id changed");
        require(jobs[index].value == original[index].value, "input value changed");
        require(jobs[index].failure == original[index].failure, "input failure changed");
    }
    require(result.outcomes.size() == jobs.size(), "outcome count mismatch");
    require(result.max_live_scratch <= capacity, "scratch capacity exceeded");
    require(result.live_scratch_after == 0, "scratch ownership leaked");
    if (jobs.size() >= 16 && capacity >= 2) {
        require(result.max_live_scratch >= 2, "pipeline was globally serialized");
    }

    for (std::size_t index = 0; index != jobs.size(); ++index) {
        const PipelineJob& job = jobs[index];
        const PipelineOutcome& outcome = result.outcomes[index];
        require(outcome.id == job.id, "outcomes are missing or out of input order");
        if (job.failure == FailurePoint::transform) {
            require(!outcome.success, "transform failure reported success");
            require(outcome.value == 0, "transform failure retained a value");
            require(outcome.error == "transform", "wrong transform error");
        } else if (job.failure == FailurePoint::persist) {
            require(!outcome.success, "persist failure reported success");
            require(outcome.value == 0, "persist failure retained a value");
            require(outcome.error == "persist", "wrong persist error");
        } else {
            require(outcome.success, "successful job reported failure");
            require(outcome.value == job.value * 2 + 3, "successful value mismatch");
            require(outcome.error.empty(), "successful job has an error");
        }
    }
}

}  // namespace

int main() {
    verify_batch({}, 3);
    verify_batch({{7, 5, FailurePoint::none}}, 1);

    std::vector<PipelineJob> jobs;
    for (int index = 0; index != 96; ++index) {
        FailurePoint failure = FailurePoint::none;
        if (index % 13 == 0) {
            failure = FailurePoint::transform;
        } else if (index % 11 == 0) {
            failure = FailurePoint::persist;
        }
        jobs.push_back(PipelineJob{1000 - index, index - 37, failure});
    }
    for (const std::size_t capacity : {1U, 2U, 4U}) {
        verify_batch(jobs, capacity);
        verify_batch(jobs, capacity);
    }

    bool rejected_zero = false;
    try {
        (void)run_pipeline(jobs, 0);
    } catch (const std::invalid_argument&) {
        rejected_zero = true;
    }
    require(rejected_zero, "zero capacity was not rejected");

    std::cout << "oneTBB bounded failure flow verifier passed\n";
}
