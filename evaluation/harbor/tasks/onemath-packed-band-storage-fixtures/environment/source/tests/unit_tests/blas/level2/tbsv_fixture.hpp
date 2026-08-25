#pragma once

#include "../include/test_common.hpp"

namespace onemath_fixture {

template <typename fp>
std::vector<fp> prepare_tbsv_matrix(layout order, uplo, transpose trans, int n, int, int lda) {
    std::vector<fp> matrix;
    rand_trsm_matrix(matrix, order, trans, n, n, lda);
    return matrix;
}

} // namespace onemath_fixture
