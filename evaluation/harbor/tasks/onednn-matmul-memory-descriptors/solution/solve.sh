#!/bin/bash
set -euo pipefail

cp /solution/batched_matmul.cpp /app/batched_matmul.cpp
bash /tests/test.sh
