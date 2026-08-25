#include "pipeline.hpp"

#include "sycl_stage.hpp"

int run_transform_pipeline(
    int count,
    int seed,
    int scale,
    long long *checksum,
    char *device_name,
    std::size_t device_name_size) {
    long long raw_checksum = 0;
    const int status = run_sycl_stage(
        count, seed, &raw_checksum, device_name, device_name_size);
    if (status != 0) return status;
    *checksum = raw_checksum * scale + static_cast<long long>(count) * 3;
    return 0;
}
