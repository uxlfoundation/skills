#!/usr/bin/env bash
set -euo pipefail

g++ -std=c++17 -O2 -Wall -Wextra -Werror \
    -I/app/oneCCL/include \
    /app/oneCCL/src/coll/algorithms/alltoallv.cpp \
    /app/reproduce.cpp \
    -o /tmp/oneccl-zero-count-public

/tmp/oneccl-zero-count-public
