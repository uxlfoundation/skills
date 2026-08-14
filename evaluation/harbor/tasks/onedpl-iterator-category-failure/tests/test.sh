#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

if ! sha256sum --check --status /opt/reproducer.sha256; then
    echo "The public reproducer was modified."
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

passed=1
if ! timeout 120 /app/reproduce.sh; then
    passed=0
fi

if ! g++ -std=c++17 -O2 -pthread \
        -I/app/oneDPL/include \
        /tests/hidden.cpp \
        -ltbb \
        -o /tmp/onedpl-no-comma-hidden; then
    passed=0
elif ! timeout 120 /tmp/onedpl-no-comma-hidden; then
    passed=0
fi

echo "$passed" > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
