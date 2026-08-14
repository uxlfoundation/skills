Repair the triangular packed- and band-storage fixture regression in the pinned historical oneMath BLAS tests under `/app/oneMath`.

The public reproducer shows that the TPSV fixture supplies a dense matrix instead of packed storage and that the TBSV fixture does not place the diagonal in the required band row. Preserve the immutable dense generator in `/app/immutable/fixture_support.hpp`; repair the editable test helpers and call sites instead.

Make the fix general across row- and column-major layouts, upper and lower triangles, transpose modes, matrix sizes, band widths, and valid leading dimensions. Do not special-case the public dimensions or weaken the checks. Run `/app/reproduce.sh` before and after the repair, then briefly explain the storage-contract error, repair, and verification.
