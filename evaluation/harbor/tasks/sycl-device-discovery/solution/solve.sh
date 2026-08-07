#!/bin/bash
set -euo pipefail
python /app/sycl_probe.py > /app/sycl-probe.json
cp /solution/diagnosis.md /app/diagnosis.md
