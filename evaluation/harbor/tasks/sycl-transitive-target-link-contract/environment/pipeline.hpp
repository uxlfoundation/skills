#pragma once

#include <cstddef>

int run_transform_pipeline(
    int count,
    int seed,
    int scale,
    long long *checksum,
    char *device_name,
    std::size_t device_name_size);
