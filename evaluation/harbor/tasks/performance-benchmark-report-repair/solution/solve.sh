#!/bin/bash
set -euo pipefail
cp /solution/report_benchmark.py /app/report_benchmark.py
bash /tests/test.sh
