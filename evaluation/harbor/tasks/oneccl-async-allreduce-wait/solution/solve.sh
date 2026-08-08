#!/bin/bash
set -euo pipefail
cp /solution/async_allreduce_pipeline.py /app/async_allreduce_pipeline.py
bash /tests/test.sh
