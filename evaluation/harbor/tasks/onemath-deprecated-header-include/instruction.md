Repair the installed-header failure in `/app/vendor/oneMath/include/oneapi/mkl.hpp`.

This project must continue to preprocess the deprecated `oneapi/mkl.hpp` compatibility header while downstream users migrate to `oneapi/math.hpp`. The current vendored header fails with `fatal error: namespace_alias.hpp: No such file or directory` even though its namespace-alias header is installed elsewhere in the include tree.

Preserve the compatibility header, its oneMath domain includes, and the `oneapi::mkl` namespace alias. Do not change `/app/smoke.cpp` or replace its public include. Run `/app/reproduce.sh` before and after the repair, then briefly explain the failure phase, root cause, change, and verification.
