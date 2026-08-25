#pragma once

#include <cstddef>

int run_sycl_stage(
    int count,
    int seed,
    long long *raw_checksum,
    char *device_name,
    std::size_t device_name_size);
