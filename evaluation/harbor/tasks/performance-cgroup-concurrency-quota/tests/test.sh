#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if g++ -std=c++17 -O2 -pthread /app/quota_parallel.cpp -ltbb -o /tmp/quota_parallel \
  && python3 /tests/verify.py /tmp/quota_parallel; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
