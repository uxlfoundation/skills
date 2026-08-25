#!/bin/bash
set -euo pipefail
python3 /app/sycl_probe.py --output /app/sycl-probe.json
cp /solution/diagnosis.md /app/diagnosis.md
