#pragma once

#include <cstddef>
#include <vector>

namespace oneccl_incident {

struct buffer_slice {
    const std::byte* data = nullptr;
    std::size_t capacity = 0;
    std::size_t offset = 0;

    void set(const std::byte* base, std::size_t total_bytes, std::size_t byte_offset) {
        data = base ? base + byte_offset : nullptr;
        capacity = total_bytes;
        offset = byte_offset;
    }
};

struct topology_slices {
    std::vector<buffer_slice> send;
    std::vector<buffer_slice> recv;
    std::vector<buffer_slice> temporary;
};

topology_slices build_topo_alltoallv_slices(const std::byte* send_base,
                                             const std::byte* recv_base,
                                             const std::vector<std::size_t>& send_counts,
                                             const std::vector<std::size_t>& recv_counts,
                                             std::size_t datatype_size,
                                             bool is_inplace);

} // namespace oneccl_incident
