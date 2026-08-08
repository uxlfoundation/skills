#!/bin/bash
set -euo pipefail
cp /solution/answer.md /app/answer.md
bash /tests/test.sh
