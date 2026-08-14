#!/bin/bash
set -euo pipefail

cp /solution/benchmark.py /app/benchmark.py
bash /tests/test.sh
