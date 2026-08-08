#!/bin/bash
set -euo pipefail
cp /solution/compare_reduction.py /app/compare_reduction.py
bash /tests/test.sh
