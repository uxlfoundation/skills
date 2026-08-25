#!/bin/bash
set -euo pipefail

cp /solution/CMakeLists.txt /app/CMakeLists.txt
cp /solution/diagnosis.md /app/diagnosis.md
bash /tests/test.sh
