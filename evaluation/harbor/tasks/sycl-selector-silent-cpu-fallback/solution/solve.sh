#!/bin/bash
set -euo pipefail
cp /solution/validate_sycl_run.py /app/validate_sycl_run.py
bash /tests/test.sh
