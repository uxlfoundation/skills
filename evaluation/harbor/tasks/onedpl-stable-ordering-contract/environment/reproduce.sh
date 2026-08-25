#!/bin/bash
set -euo pipefail
g++ -std=c++17 -O2 -pthread -I/opt/onedpl/include /app/order_events.cpp -ltbb -o /tmp/order_events
/tmp/order_events 257 7 > /tmp/public-order.txt
python3 - /tmp/public-order.txt 257 <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
expected_count = int(sys.argv[2])
pairs = [tuple(map(int, line.split(":"))) for line in lines]
keys = [key for key, _ in pairs]
arrivals = [arrival for _, arrival in pairs]
assert len(pairs) == expected_count
assert keys == sorted(keys)
assert sorted(arrivals) == list(range(expected_count))
for previous, current in zip(pairs, pairs[1:]):
    if previous[0] == current[0]:
        assert previous[1] < current[1], (previous, current)
print("public stable-order contract passed")
PY
