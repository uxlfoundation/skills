#pragma once

#include "../include/test_common.hpp"

namespace onemath_fixture {

template <typename fp>
std::vector<fp> prepare_tbsv_matrix(layout order, uplo triangle, transpose trans,
                                    int n, int k, int lda) {
    std::vector<fp> matrix;
    rand_tbsv_matrix(matrix, order, triangle, trans, n, k, lda);
    return matrix;
}

} // namespace onemath_fixture
