#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
if grep -Eq 'oneapi::tbb::(enumerable_thread_specific|parallel_reduce)' /app/histogram.cpp \
  && g++ -std=c++17 -O2 -pthread /app/histogram.cpp /tests/verify.cpp -ltbb -o /tmp/verify \
  && /tmp/verify; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
