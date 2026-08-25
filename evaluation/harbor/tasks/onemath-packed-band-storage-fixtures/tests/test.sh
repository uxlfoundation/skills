#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

if ! sha256sum --check --status /opt/reproducer.sha256; then
    echo "The immutable fixture support or public reproducer was modified."
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

passed=1
if ! timeout 30 /app/reproduce.sh; then
    passed=0
fi

if ! g++ -std=c++17 -O2 -Wall -Wextra -Werror \
        /tests/hidden.cpp \
        -o /tmp/onemath-storage-hidden; then
    passed=0
elif ! timeout 30 /tmp/onemath-storage-hidden; then
    passed=0
fi

echo "$passed" > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
