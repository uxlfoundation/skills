#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

if python /tests/verify.py /app/report_benchmark.py; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
cat /logs/verifier/reward.txt
