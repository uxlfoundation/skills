#include "join_pipeline.h"

#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include <oneapi/tbb/global_control.h>

namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

void verify_round(std::size_t token_count) {
    const auto joined = run_join_pipeline(token_count);
    require(joined.size() == token_count, "token count changed");

    std::vector<bool> seen(token_count, false);
    for (const auto& token : joined) {
        require(token.source >= 0, "negative source token");
        const auto source = static_cast<std::size_t>(token.source);
        require(source < token_count, "source token out of range");
        require(!seen[source], "source token emitted more than once");
        require(token.counterpart == token.source, "unrelated tokens were joined");
        seen[source] = true;
    }
}

}  // namespace

int main() {
    try {
        oneapi::tbb::global_control concurrency(
            oneapi::tbb::global_control::max_allowed_parallelism, 4);

        for (int repetition = 0; repetition != 24; ++repetition) {
            verify_round(128 + static_cast<std::size_t>(repetition % 5) * 31);
        }
        verify_round(1);
        verify_round(2);
    } catch (const std::exception& error) {
        std::cerr << "verification failed: " << error.what() << '\n';
        return 1;
    }

    std::cout << "oneTBB join-node ordering verifier passed\n";
}
