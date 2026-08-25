#include <sycl/sycl.hpp>

#include <array>
#include <exception>
#include <iostream>

int main() {
    try {
        sycl::queue queue{sycl::gpu_selector_v};
        constexpr std::size_t count = 256;
        std::array<int, count> values{};
        for (std::size_t index = 0; index < count; ++index) {
            values[index] = static_cast<int>(index);
        }

        {
            sycl::buffer<int, 1> buffer{values.data(), sycl::range<1>{count}};
            queue.submit([&](sycl::handler& handler) {
                auto data = buffer.get_access<sycl::access::mode::read_write>(handler);
                handler.parallel_for(sycl::range<1>{count}, [=](sycl::id<1> index) {
                    data[index] = 3 * data[index] + 7;
                });
            });
            queue.wait_and_throw();
        }

        for (std::size_t index = 0; index < count; ++index) {
            const int expected = 3 * static_cast<int>(index) + 7;
            if (values[index] != expected) {
                std::cerr << "result=fail index=" << index
                          << " expected=" << expected
                          << " observed=" << values[index] << '\n';
                return 2;
            }
        }

        const sycl::device device = queue.get_device();
        std::cout << "device_name="
                  << device.get_info<sycl::info::device::name>() << '\n';
        std::cout << "device_vendor="
                  << device.get_info<sycl::info::device::vendor>() << '\n';
        std::cout << "device_type=gpu\n";
        std::cout << "result=pass\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "result=error message=" << error.what() << '\n';
        return 1;
    }
}
