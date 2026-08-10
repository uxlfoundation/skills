#!/bin/bash
set -euo pipefail
cp /solution/pipeline.cpp /app/pipeline.cpp
bash /tests/test.sh
