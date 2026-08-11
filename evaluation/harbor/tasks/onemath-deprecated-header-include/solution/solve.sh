#!/bin/bash
set -euo pipefail

sed -i 's|#include "namespace_alias.hpp"|#include "mkl/namespace_alias.hpp"|' \
  /app/vendor/oneMath/include/oneapi/mkl.hpp
bash /tests/test.sh
