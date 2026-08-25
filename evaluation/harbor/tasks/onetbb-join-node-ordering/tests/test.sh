#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if g++ -std=c++17 -O0 -pthread -I/app /app/join_pipeline.cpp /tests/verify.cpp -ltbb -o /tmp/verify \
  && timeout 30 /tmp/verify \
  && grep -Eq '(sequencer_node|key_matching)' /app/join_pipeline.cpp \
  && ! grep -Eq '(max_allowed_parallelism|task_arena[[:space:]]*\([^,]*1)' /app/join_pipeline.cpp; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
