#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/sycl-link-protected.sha256 || {
    echo "Protected source or reproduction files were modified."
    exit 1
}

test -s /app/CMakeLists.txt
test -s /app/diagnosis.md

python3 - <<'PY'
from pathlib import Path

text = Path('/app/diagnosis.md').read_text(encoding='utf-8').lower()
assert 'link' in text, 'diagnosis must classify the link phase'
assert 'g++' in text, 'diagnosis must identify the host-only link driver'
assert 'icpx' in text or 'dpc++' in text, 'diagnosis must identify the SYCL-capable driver'
assert '-fsycl' in text, 'diagnosis must describe the SYCL link contract'
assert 'device' in text or 'runtime' in text, 'diagnosis must discuss runtime/device verification'
PY

bash /app/reproduce.sh

binary=/tmp/uxl-sycl-link-public/sycl_probe
test -x "${binary}"
nm -C "${binary}" | grep -q 'run_sycl_transform'
ldd "${binary}" | grep -q 'libsycl'

python3 - <<'PY'
import json
import os
from pathlib import Path
import subprocess

binary = '/tmp/uxl-sycl-link-public/sycl_probe'
selector = os.environ.get('UXL_SYCL_SELECTOR', '')
environment = os.environ.copy()
if selector:
    environment['ONEAPI_DEVICE_SELECTOR'] = selector


def expected_checksum(count, seed):
    return sum((((index * 17 + seed) % 97) * 3 + 1) for index in range(count))


def run_case(count, seed):
    output = subprocess.check_output(
        [binary, str(count), str(seed)], text=True, env=environment
    )
    values = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
    assert values.get('status') == 'ok', values
    assert values.get('device'), values
    assert int(values['count']) == count, values
    assert int(values['seed']) == seed, values
    assert int(values['checksum']) == expected_checksum(count, seed), values
    assert int(values['expected']) == expected_checksum(count, seed), values
    return values['device']


cases = ((1, 0), (257, 29), (8193, 61), (16384, 7))
devices = [run_case(*case) for case in cases]
reward = {'reward': 1.0, 'hidden_cases': len(cases), 'devices': sorted(set(devices))}
Path('/logs/verifier/reward.json').write_text(
    json.dumps(reward, indent=2) + '\n', encoding='utf-8'
)
print(json.dumps(reward, indent=2))
PY
