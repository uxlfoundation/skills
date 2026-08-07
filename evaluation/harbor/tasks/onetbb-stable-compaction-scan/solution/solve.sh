#!/bin/bash
set -euo pipefail
cp /solution/stable_compact.cpp /app/stable_compact.cpp
bash /tests/test.sh
