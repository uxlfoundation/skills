#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if grep -Eq '(oneapi::tbb::|tbb::)parallel_reduce[[:space:]]*\(' /app/runtime_composition.cpp \
  && grep -Eq '(^|[^[:alnum:]_])task_arena([^[:alnum:]_]|$)' /app/runtime_composition.cpp \
  && grep -Eq '\.(execute|enqueue)[[:space:]]*\(' /app/runtime_composition.cpp \
  && g++ -std=c++17 -O2 -pthread -I/app /app/runtime_composition.cpp /tests/verify.cpp -ltbb -o /tmp/verify \
  && timeout 30 /tmp/verify; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
