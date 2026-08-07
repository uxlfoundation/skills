#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if grep -Eq '(oneapi::tbb::|tbb::)parallel_scan[[:space:]]*\(' /app/stable_compact.cpp \
  && ! grep -Eq 'std::(atomic|mutex)' /app/stable_compact.cpp \
  && g++ -std=c++17 -O2 -pthread /app/stable_compact.cpp /tests/verify.cpp -ltbb -o /tmp/verify \
  && /tmp/verify; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
