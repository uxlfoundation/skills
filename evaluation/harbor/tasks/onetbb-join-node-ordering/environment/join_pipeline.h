#pragma once

#include <cstddef>
#include <vector>

struct JoinedToken {
    int source;
    int counterpart;
};

std::vector<JoinedToken> run_join_pipeline(std::size_t token_count);
