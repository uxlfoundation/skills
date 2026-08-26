#!/bin/bash
set -euo pipefail
cp /solution/runtime.cmake /app/runtime.cmake
cp /solution/diagnosis.md /app/diagnosis.md
bash /tests/test.sh
