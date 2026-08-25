#!/bin/bash
set -euo pipefail
cp /solution/join_pipeline.cpp /app/join_pipeline.cpp
bash /tests/test.sh
