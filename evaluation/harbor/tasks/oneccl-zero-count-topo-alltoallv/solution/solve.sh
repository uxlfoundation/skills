#!/usr/bin/env bash
set -euo pipefail

cp /solution/alltoallv.cpp /app/oneCCL/src/coll/algorithms/alltoallv.cpp
bash /tests/test.sh
