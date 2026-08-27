#include "oneccl_incident/alltoallv_model.hpp"

#include <numeric>
#include <stdexcept>

namespace oneccl_incident {
namespace {

std::vector<std::size_t> byte_offsets(const std::vector<std::size_t>& counts,
                                      std::size_t datatype_size) {
    std::vector<std::size_t> offsets(counts.size(), 0);
    for (std::size_t index = 1; index < counts.size(); ++index) {
        offsets[index] = offsets[index - 1] + counts[index - 1] * datatype_size;
    }
    return offsets;
}

std::size_t total_bytes(const std::vector<std::size_t>& counts, std::size_t datatype_size) {
    return std::accumulate(counts.begin(), counts.end(), std::size_t{0}) * datatype_size;
}

} // namespace

topology_slices build_topo_alltoallv_slices(const std::byte* send_base,
                                             const std::byte* recv_base,
                                             const std::vector<std::size_t>& send_counts,
                                             const std::vector<std::size_t>& recv_counts,
                                             std::size_t datatype_size,
                                             bool is_inplace) {
    if (send_counts.size() != recv_counts.size() || datatype_size == 0) {
        throw std::invalid_argument("incompatible alltoallv shape");
    }

    const auto send_offsets = byte_offsets(send_counts, datatype_size);
    const auto recv_offsets = byte_offsets(recv_counts, datatype_size);
    const auto send_bytes = total_bytes(send_counts, datatype_size);
    const auto recv_bytes = total_bytes(recv_counts, datatype_size);

    topology_slices result;
    result.send.resize(send_counts.size());
    result.recv.resize(recv_counts.size());

    if (is_inplace) {
        if (send_counts != recv_counts) {
            throw std::invalid_argument("in-place counts must match");
        }
        for (std::size_t index = 0; index < recv_counts.size(); ++index) {
            if (recv_counts[index] == 0) {
                result.recv[index].set(nullptr, 0, 0);
            }
            else {
                result.recv[index].set(send_base, recv_bytes, recv_offsets[index]);
            }
            result.send[index] = result.recv[index];
        }

        result.temporary.resize(send_counts.size());
        for (std::size_t index = 0; index < send_counts.size(); ++index) {
            if (send_counts[index] == 0) {
                result.temporary[index].set(nullptr, 0, 0);
            }
            else {
                result.temporary[index].set(
                    send_base, send_counts[index] * datatype_size, 0);
            }
        }
    }
    else {
        for (std::size_t index = 0; index < send_counts.size(); ++index) {
            if (send_counts[index] == 0) {
                result.send[index].set(nullptr, 0, 0);
            }
            else {
                result.send[index].set(send_base, send_bytes, send_offsets[index]);
            }

            if (recv_counts[index] == 0) {
                result.recv[index].set(nullptr, 0, 0);
            }
            else {
                result.recv[index].set(recv_base, recv_bytes, recv_offsets[index]);
            }
        }
    }

    return result;
}

} // namespace oneccl_incident
