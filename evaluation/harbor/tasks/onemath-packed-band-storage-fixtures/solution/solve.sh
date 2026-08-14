#!/usr/bin/env bash
set -euo pipefail

cp -R /solution/fixed/. /app/oneMath/
bash /tests/test.sh
