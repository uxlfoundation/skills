#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

if ! sha256sum --check --status /opt/reproducer.sha256; then
    echo "The reproducer contract or model interface was modified."
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

passed=1
if ! timeout 60 /app/reproduce.sh; then
    passed=0
fi

if ! g++ -std=c++17 -O2 -Wall -Wextra -Werror \
        -I/app/oneCCL/include \
        /app/oneCCL/src/coll/algorithms/alltoallv.cpp \
        /tests/hidden.cpp \
        -o /tmp/oneccl-zero-count-hidden; then
    passed=0
elif ! timeout 60 /tmp/oneccl-zero-count-hidden; then
    passed=0
fi

echo "$passed" > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
