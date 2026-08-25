#include "/app/oneMath/tests/unit_tests/blas/level2/tbsv_fixture.hpp"
#include "/app/oneMath/tests/unit_tests/blas/level2/tpsv_fixture.hpp"

#include <algorithm>
#include <cstddef>
#include <iostream>
#include <vector>

using namespace onemath_fixture;

template <typename fp>
std::vector<fp> expected_packed(layout order, uplo triangle, transpose trans, int n) {
    std::vector<fp> dense;
    rand_trsm_matrix(dense, order, trans, n, n, n);
    std::vector<fp> expected;
    expected.reserve(std::size_t(n * (n + 1) / 2));

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
            expected.push_back(dense[std::size_t(row + column * n)]);
        }
    }
    return expected;
}

template <typename fp>
std::vector<fp> expected_band(layout order, uplo triangle, transpose trans, int n, int k, int lda) {
    std::vector<fp> dense;
    rand_trsm_matrix(dense, order, trans, n, n, lda);
    std::vector<fp> expected(std::size_t(matrix_size(order, trans, n, n, lda)), fp{});

    const bool upper_storage =
        (order == layout::column_major && triangle == uplo::U) ||
        (order == layout::row_major && triangle == uplo::L);
    for (int column = 0; column < n; ++column) {
        if (upper_storage) {
            const int offset = k - column;
            for (int row = std::max(0, column - k); row <= column; ++row) {
                expected[std::size_t(offset + row + column * lda)] =
                    dense[std::size_t(row + column * lda)];
            }
        } else {
            const int offset = -column;
            for (int row = column; row < std::min(n, column + k + 1); ++row) {
                expected[std::size_t(offset + row + column * lda)] =
                    dense[std::size_t(row + column * lda)];
            }
        }
    }
    return expected;
}

int main() {
    bool ok = true;
    int cases = 0;
    for (const auto order : { layout::column_major, layout::row_major }) {
        for (const auto triangle : { uplo::U, uplo::L }) {
            for (const auto trans : { transpose::nontrans, transpose::trans }) {
                for (const int n : { 1, 4, 9 }) {
                    const auto packed = prepare_tpsv_matrix<double>(order, triangle, trans, n);
                    const auto packed_reference = expected_packed<double>(order, triangle, trans, n);
                    ok &= packed == packed_reference;

                    const int k = n == 1 ? 0 : std::min(3, n - 1);
                    const int lda = n + 5;
                    const auto band = prepare_tbsv_matrix<double>(order, triangle, trans, n, k, lda);
                    const auto band_reference = expected_band<double>(order, triangle, trans, n, k, lda);
                    ok &= band == band_reference;
                    ++cases;
                }
            }
        }
    }

    std::cout << "held_out_cases=" << cases << " result=" << (ok ? "pass" : "fail") << '\n';
    return ok ? 0 : 1;
}
