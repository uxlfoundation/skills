#pragma once

#include "/app/immutable/fixture_support.hpp"

#include <algorithm>
#include <vector>

namespace onemath_fixture {

template <typename vec>
void rand_tpsv_matrix(vec& matrix, layout order, uplo triangle, transpose trans, int n) {
    using fp = typename vec::value_type;
    std::vector<fp> dense;
    rand_trsm_matrix(dense, order, trans, n, n, n);
    matrix.resize(static_cast<std::size_t>(n * (n + 1) / 2));

    int output = 0;
    for (int column = 0; column < n; ++column) {
        int first;
        int last;
        if (order == layout::column_major) {
            first = triangle == uplo::U ? 0 : column;
            last = triangle == uplo::U ? column : n - 1;
        } else {
            first = triangle == uplo::U ? column : 0;
            last = triangle == uplo::U ? n - 1 : column;
        }
        for (int row = first; row <= last; ++row) {
            matrix[static_cast<std::size_t>(output++)] =
                dense[static_cast<std::size_t>(row + column * n)];
        }
    }
}

template <typename vec>
void rand_tbsv_matrix(vec& matrix, layout order, uplo triangle, transpose trans,
                      int n, int k, int lda) {
    using fp = typename vec::value_type;
    std::vector<fp> dense;
    rand_trsm_matrix(dense, order, trans, n, n, lda);
    matrix.assign(static_cast<std::size_t>(matrix_size(order, trans, n, n, lda)), fp{});

    const bool upper_storage =
        (order == layout::column_major && triangle == uplo::U) ||
        (order == layout::row_major && triangle == uplo::L);
    for (int column = 0; column < n; ++column) {
        if (upper_storage) {
            const int offset = k - column;
            for (int row = std::max(0, column - k); row <= column; ++row) {
                matrix[static_cast<std::size_t>(offset + row + column * lda)] =
                    dense[static_cast<std::size_t>(row + column * lda)];
            }
        } else {
            const int offset = -column;
            for (int row = column; row < std::min(n, column + k + 1); ++row) {
                matrix[static_cast<std::size_t>(offset + row + column * lda)] =
                    dense[static_cast<std::size_t>(row + column * lda)];
            }
        }
    }
}

} // namespace onemath_fixture
