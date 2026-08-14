#include <array>
#include <iostream>
#include <sycl/sycl.hpp>

int main() {
    std::array<int, 4> values {1, 2, 3, 4};
    sycl::queue queue;

    {
        sycl::buffer<int> buffer(values.data(), sycl::range<1>(values.size()));
        queue.submit([&](sycl::handler &handler) {
            sycl::accessor data(buffer, handler, sycl::read_write);
            handler.parallel_for(sycl::range<1>(values.size()), [=](sycl::id<1> index) {
                data[index] *= 2;
            });
        });
    }

    if (values != std::array<int, 4> {2, 4, 6, 8}) return 1;

    std::cout << queue.get_device().get_info<sycl::info::device::name>() << '\n';
    return 0;
}
