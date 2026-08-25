#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path

path = Path("/app/order_events.cpp")
source = path.read_text(encoding="utf-8")
old = "std::sort(oneapi::dpl::execution::par,"
new = "std::stable_sort(oneapi::dpl::execution::par,"
if source.count(old) != 1:
    raise SystemExit("expected one oneDPL sort call")
path.write_text(source.replace(old, new), encoding="utf-8")
PY
bash /tests/test.sh
