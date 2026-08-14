#pragma once

#include "../include/test_common.hpp"

namespace onemath_fixture {

template <typename fp>
std::vector<fp> prepare_tpsv_matrix(layout order, uplo triangle, transpose trans, int n) {
    std::vector<fp> matrix;
    rand_tpsv_matrix(matrix, order, triangle, trans, n);
    return matrix;
}

} // namespace onemath_fixture
