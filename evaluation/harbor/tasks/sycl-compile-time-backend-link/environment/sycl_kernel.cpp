#include <algorithm>
#include <cstddef>
#include <cstring>
#include <string>
#include <vector>

#include <sycl/sycl.hpp>

extern "C" int run_sycl_transform(
    int count,
    int seed,
    long long *checksum,
    char *device_name,
    std::size_t device_name_size) {
    try {
        sycl::queue queue;
        std::vector<int> values(static_cast<std::size_t>(count));

        {
            sycl::buffer<int> buffer(values.data(), sycl::range<1>(values.size()));
            queue.submit([&](sycl::handler &handler) {
                sycl::accessor output(buffer, handler, sycl::write_only, sycl::no_init);
                handler.parallel_for(sycl::range<1>(values.size()), [=](sycl::id<1> item) {
                    const int index = static_cast<int>(item[0]);
                    output[item] = ((index * 17 + seed) % 97) * 3 + 1;
                });
            });
        }

        long long total = 0;
        for (const int value : values) total += value;
        *checksum = total;

        const std::string name = queue.get_device().get_info<sycl::info::device::name>();
        if (device_name_size > 0) {
            const std::size_t copied = std::min(name.size(), device_name_size - 1);
            std::memcpy(device_name, name.data(), copied);
            device_name[copied] = '\0';
        }
        return 0;
    } catch (const sycl::exception &) {
        return 1;
    }
}
