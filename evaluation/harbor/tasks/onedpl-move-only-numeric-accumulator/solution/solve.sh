#!/usr/bin/env bash
set -euo pipefail

tar -xzf /solution/onedpl-fixed-include.tar.gz -C /app/oneDPL
bash /tests/test.sh
