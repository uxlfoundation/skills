#include "oneccl_incident/alltoallv_model.hpp"

#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <vector>

int main() {
    constexpr std::size_t neighbor_count = 4096;
    std::vector<std::byte> send(neighbor_count * sizeof(float));
    std::vector<std::byte> recv(neighbor_count * sizeof(float));

    const std::vector<std::size_t> send_counts{neighbor_count, 0};
    const std::vector<std::size_t> recv_counts{0, neighbor_count};
    const auto slices = oneccl_incident::build_topo_alltoallv_slices(
        send.data(), recv.data(), send_counts, recv_counts, sizeof(float), false);

    if (slices.send[1].data != nullptr || slices.send[1].capacity != 0 ||
        slices.send[1].offset != 0) {
        throw std::runtime_error("zero-count send slice retains a one-past pointer");
    }
    if (slices.recv[0].data != nullptr || slices.recv[0].capacity != 0 ||
        slices.recv[0].offset != 0) {
        throw std::runtime_error("zero-count receive slice is not null and empty");
    }
    if (slices.send[0].data != send.data() || slices.recv[1].data != recv.data()) {
        throw std::runtime_error("live neighbor slice changed");
    }

    std::cout << "UXL_ZERO_COUNT_TOPO_ALLTOALLV=PASS\n";
    return 0;
}
