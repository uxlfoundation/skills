#include "/app/oneMath/tests/unit_tests/blas/level2/tbsv_fixture.hpp"
#include "/app/oneMath/tests/unit_tests/blas/level2/tpsv_fixture.hpp"

#include <cstddef>
#include <iostream>

using namespace onemath_fixture;

int main() {
    bool ok = true;

    constexpr int packed_n = 5;
    const auto packed = prepare_tpsv_matrix<double>(layout::column_major, uplo::U,
                                                     transpose::nontrans, packed_n);
    const std::size_t expected_packed_size = packed_n * (packed_n + 1) / 2;
    std::cout << "packed_size=" << packed.size() << " expected=" << expected_packed_size << '\n';
    ok &= packed.size() == expected_packed_size;
    if (packed.size() >= expected_packed_size) {
        ok &= packed[0] == fixture_value<double>(0, 0);
        ok &= packed[2] == fixture_value<double>(1, 1);
        ok &= packed[expected_packed_size - 1] == fixture_value<double>(4, 4);
    }

    constexpr int band_n = 7;
    constexpr int band_k = 2;
    constexpr int band_lda = 9;
    const auto band = prepare_tbsv_matrix<double>(layout::row_major, uplo::L, transpose::trans,
                                                   band_n, band_k, band_lda);
    bool diagonal_ok = band.size() == std::size_t(band_n * band_lda);
    if (diagonal_ok) {
        for (int column = 0; column < band_n; ++column) {
            diagonal_ok &= band[std::size_t(band_k + column * band_lda)] ==
                           fixture_value<double>(column, column);
        }
    }
    std::cout << "band_diagonal=" << (diagonal_ok ? "ok" : "wrong") << '\n';
    ok &= diagonal_ok;

    return ok ? 0 : 1;
}
