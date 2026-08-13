#!/usr/bin/env bash
set -euo pipefail
sed '/__attribute__((__assume__(iStart < std::numeric_limits<std::ptrdiff_t>::max())));/d' \
    /solution/df_regression_train_dense_default_impl.i > \
   /app/oneDAL/cpp/daal/src/algorithms/dtrees/forest/regression/df_regression_train_dense_default_impl.i
bash /tests/test.sh
