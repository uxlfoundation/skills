#!/bin/bash
set -euo pipefail
cp /solution/runtime_composition.cpp /app/runtime_composition.cpp
bash /tests/test.sh
