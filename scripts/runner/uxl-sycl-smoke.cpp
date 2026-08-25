#include <sycl/sycl.hpp>
#include <iostream>

int main() {
  sycl::queue q;
  int result = 0;
  {
    sycl::buffer<int> b(&result, sycl::range<1>(1));
    q.submit([&](sycl::handler& h) {
      auto out = b.get_access<sycl::access::mode::write>(h);
      h.single_task([=]() { out[0] = 42; });
    });
  }
  std::cout << q.get_device().get_info<sycl::info::device::name>() << "\n";
  std::cout << result << "\n";
  return result == 42 ? 0 : 1;
}
