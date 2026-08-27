#include "oneccl_incident/alltoallv_model.hpp"

#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {

std::vector<std::size_t> offsets(const std::vector<std::size_t>& counts,
                                 std::size_t datatype_size) {
    std::vector<std::size_t> result(counts.size(), 0);
    for (std::size_t index = 1; index < counts.size(); ++index) {
        result[index] = result[index - 1] + counts[index - 1] * datatype_size;
    }
    return result;
}

std::size_t total(const std::vector<std::size_t>& counts, std::size_t datatype_size) {
    std::size_t result = 0;
    for (const auto count : counts) result += count * datatype_size;
    return result;
}

void check_slice(const oneccl_incident::buffer_slice& slice,
                 const std::byte* base,
                 std::size_t total_bytes,
                 std::size_t byte_offset,
                 std::size_t count) {
    if (count == 0) {
        if (slice.data != nullptr || slice.capacity != 0 || slice.offset != 0) {
            throw std::runtime_error("zero-count slice is not canonical null/empty");
        }
    }
    else if (slice.data != base + byte_offset || slice.capacity != total_bytes ||
             slice.offset != byte_offset) {
        throw std::runtime_error("live slice metadata changed");
    }
}

void check_out_of_place(const std::vector<std::size_t>& send_counts,
                        const std::vector<std::size_t>& recv_counts,
                        std::size_t datatype_size) {
    std::vector<std::byte> send(total(send_counts, datatype_size) + 1);
    std::vector<std::byte> recv(total(recv_counts, datatype_size) + 1);
    const auto result = oneccl_incident::build_topo_alltoallv_slices(
        send.data(), recv.data(), send_counts, recv_counts, datatype_size, false);
    const auto send_offsets = offsets(send_counts, datatype_size);
    const auto recv_offsets = offsets(recv_counts, datatype_size);
    for (std::size_t index = 0; index < send_counts.size(); ++index) {
        check_slice(result.send[index],
                    send.data(),
                    total(send_counts, datatype_size),
                    send_offsets[index],
                    send_counts[index]);
        check_slice(result.recv[index],
                    recv.data(),
                    total(recv_counts, datatype_size),
                    recv_offsets[index],
                    recv_counts[index]);
    }
}

void check_inplace(const std::vector<std::size_t>& counts, std::size_t datatype_size) {
    std::vector<std::byte> buffer(total(counts, datatype_size) + 1);
    const auto result = oneccl_incident::build_topo_alltoallv_slices(
        buffer.data(), buffer.data(), counts, counts, datatype_size, true);
    const auto byte_offsets = offsets(counts, datatype_size);
    for (std::size_t index = 0; index < counts.size(); ++index) {
        check_slice(result.send[index],
                    buffer.data(),
                    total(counts, datatype_size),
                    byte_offsets[index],
                    counts[index]);
        check_slice(result.recv[index],
                    buffer.data(),
                    total(counts, datatype_size),
                    byte_offsets[index],
                    counts[index]);
        if (counts[index] == 0) {
            check_slice(result.temporary[index], buffer.data(), 0, 0, 0);
        }
        else if (result.temporary[index].data == nullptr ||
                 result.temporary[index].capacity != counts[index] * datatype_size ||
                 result.temporary[index].offset != 0) {
            throw std::runtime_error("live temporary slice changed");
        }
    }
}

} // namespace

int main() {
    check_out_of_place({0, 3, 0, 5, 0}, {2, 0, 0, 6, 0}, sizeof(double));
    check_out_of_place({0, 0, 0}, {0, 0, 0}, sizeof(float));
    check_out_of_place({7, 0, 9}, {0, 11, 5}, sizeof(short));
    check_inplace({0, 4, 0, 2, 0}, sizeof(float));
    check_inplace({0, 0}, sizeof(double));
    std::cout << "UXL_ZERO_COUNT_HIDDEN=PASS\n";
    return 0;
}
