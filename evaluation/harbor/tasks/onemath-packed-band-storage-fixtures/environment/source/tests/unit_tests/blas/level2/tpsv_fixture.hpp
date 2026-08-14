#pragma once

#include "../include/test_common.hpp"

namespace onemath_fixture {

template <typename fp>
std::vector<fp> prepare_tpsv_matrix(layout order, uplo, transpose trans, int n) {
    std::vector<fp> matrix;
    rand_trsm_matrix(matrix, order, trans, n, n, n);
    return matrix;
}

} // namespace onemath_fixture
