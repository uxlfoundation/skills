#pragma once

#include <cstddef>
#include <vector>

namespace onemath_fixture {

enum class layout { column_major, row_major };
enum class uplo { U, L };
enum class transpose { nontrans, trans };

template <typename T>
constexpr T inner_dimension(transpose trans, T m, T n) {
    return trans == transpose::nontrans ? m : n;
}

template <typename T>
constexpr T outer_dimension(transpose trans, T m, T n) {
    return trans == transpose::nontrans ? n : m;
}

template <typename T>
constexpr T matrix_size(layout order, transpose trans, T m, T n, T ld) {
    return order == layout::column_major ? outer_dimension(trans, m, n) * ld
                                         : inner_dimension(trans, m, n) * ld;
}

template <typename fp>
constexpr fp fixture_value(int row, int column) {
    return row == column ? fp(1000 + row) : fp(1 + row * 100 + column);
}

// This is the minimized dense triangular generator from the historical test
// utility. It is immutable because the incident was repaired by adding the
// packed/band generators and selecting them at the TPSV/TBSV call sites.
template <typename vec>
void rand_trsm_matrix(vec& matrix, layout order, transpose trans, int m, int n, int ld) {
    using fp = typename vec::value_type;
    matrix.assign(static_cast<std::size_t>(matrix_size(order, trans, m, n, ld)), fp{});

    if ((trans == transpose::nontrans && order == layout::column_major) ||
        (trans != transpose::nontrans && order == layout::row_major)) {
        for (int column = 0; column < n; ++column) {
            for (int row = 0; row < m; ++row) {
                matrix[static_cast<std::size_t>(row + column * ld)] =
                    fixture_value<fp>(row, column);
            }
        }
    } else {
        for (int row = 0; row < m; ++row) {
            for (int column = 0; column < n; ++column) {
                matrix[static_cast<std::size_t>(column + row * ld)] =
                    fixture_value<fp>(row, column);
            }
        }
    }
}

} // namespace onemath_fixture
