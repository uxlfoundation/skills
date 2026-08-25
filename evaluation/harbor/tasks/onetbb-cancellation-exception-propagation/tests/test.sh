#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if grep -Eq '(^|[^[:alnum:]_])limiter_node[[:space:]]*<' /app/pipeline.cpp \
  && grep -Eq 'decrementer[[:space:]]*\(' /app/pipeline.cpp \
  && grep -Eq '(^|[^[:alnum:]_])function_node[[:space:]]*<' /app/pipeline.cpp \
  && g++ -std=c++17 -O2 -pthread -I/app /app/pipeline.cpp /tests/verify.cpp -ltbb -o /tmp/verify \
  && timeout 30 /tmp/verify; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
