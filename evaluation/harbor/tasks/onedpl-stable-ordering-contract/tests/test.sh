#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/order_events.cpp may change."
    exit 1
}

grep -Eq 'oneapi::dpl::execution::par' /app/order_events.cpp || {
    echo "The repair must preserve oneDPL's host par execution policy."
    exit 1
}

grep -Eq 'left\.key[[:space:]]*<[[:space:]]*right\.key' /app/order_events.cpp || {
    echo "The repair must preserve the key-only comparison contract."
    exit 1
}

bash /app/reproduce.sh
g++ -std=c++17 -O2 -pthread -I/opt/onedpl/include /app/order_events.cpp -ltbb -o /tmp/order_events

python3 - <<'PY'
import json
from pathlib import Path
import subprocess


def verify(count: int, key_count: int) -> None:
    output = subprocess.check_output(
        ["/tmp/order_events", str(count), str(key_count)], text=True
    )
    pairs = [tuple(map(int, line.split(":"))) for line in output.splitlines()]
    assert len(pairs) == count, len(pairs)
    assert [key for key, _ in pairs] == sorted(key for key, _ in pairs)
    assert sorted(arrival for _, arrival in pairs) == list(range(count))
    grouped: dict[int, list[int]] = {}
    for key, arrival in pairs:
        grouped.setdefault(key, []).append(arrival)
    for arrivals in grouped.values():
        assert arrivals == sorted(arrivals), arrivals


cases = [(257, 7), (1021, 13), (64, 1), (509, 37)]
for case in cases:
    verify(*case)

Path("/logs/verifier/reward.json").write_text(
    json.dumps({"reward": 1.0, "stable_cases": len(cases)}, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps({"stable_cases": cases}, indent=2))
PY
