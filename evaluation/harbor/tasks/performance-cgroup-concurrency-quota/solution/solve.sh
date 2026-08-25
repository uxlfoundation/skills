#!/bin/bash
set -euo pipefail
cp /solution/quota_parallel.cpp /app/quota_parallel.cpp
bash /tests/test.sh
