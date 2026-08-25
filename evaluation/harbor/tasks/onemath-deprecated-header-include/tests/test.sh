#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier
header=/app/vendor/oneMath/include/oneapi/mkl.hpp
domain_includes_ok=1
for domain in blas dft lapack rng sparse_blas types; do
  grep -Fq "oneapi/math/${domain}.hpp" "$header" || domain_includes_ok=0
done

if g++ -std=c++17 -E \
     -I/tests/stubs \
     -I/app/vendor/oneMath/include \
     /tests/smoke.cpp \
  -o /tmp/onemath-mkl.i \
  && grep -Eq '#include[[:space:]]*[<"](oneapi/)?mkl/namespace_alias\.hpp[>"]' "$header" \
  && [[ "$domain_includes_ok" -eq 1 ]] \
  && grep -Fq '/oneapi/mkl/namespace_alias.hpp' /tmp/onemath-mkl.i \
  && grep -Fq 'Namespace `oneapi::mkl` is deprecated' /tmp/onemath-mkl.i; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
