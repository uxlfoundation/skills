#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/sycl-transitive-protected.sha256 || {
    echo "Protected source, module, or reproduction files were modified."
    exit 1
}

test -s /app/CMakeLists.txt
test -s /app/diagnosis.md

python3 - <<'PY'
from pathlib import Path

cmake = Path('/app/CMakeLists.txt').read_text(encoding='utf-8').lower()
diagnosis = Path('/app/diagnosis.md').read_text(encoding='utf-8').lower()

for forbidden in ('cmake_cxx_flags', 'link_directories', 'libsycl', '/opt/intel'):
    assert forbidden not in cmake, f'forbidden non-target-scoped workaround: {forbidden}'

assert 'link' in diagnosis, 'diagnosis must classify the link phase'
assert 'object' in diagnosis, 'diagnosis must discuss the object-library boundary'
assert 'private' in diagnosis or 'transitive' in diagnosis or 'usage requirement' in diagnosis
assert '-fsycl' in diagnosis, 'diagnosis must explain the SYCL link contract'
assert 'device' in diagnosis or 'runtime' in diagnosis, 'diagnosis must discuss runtime evidence'
PY

bash /app/reproduce.sh

build_root=/tmp/uxl-sycl-transitive-public
binary="${build_root}/transitive_probe"
test -x "${binary}"

ninja -C "${build_root}" -t commands transitive_probe \
    > /tmp/uxl-sycl-transitive-commands.txt
python3 - <<'PY'
from pathlib import Path

lines = Path('/tmp/uxl-sycl-transitive-commands.txt').read_text(encoding='utf-8').splitlines()
links = [line for line in lines if '-o transitive_probe' in line]
assert len(links) == 1, links
assert 'icpx' in links[0], links[0]
assert '-fsycl' in links[0], links[0]
PY

ldd "${binary}" > /tmp/uxl-sycl-transitive-libraries.txt
grep -q 'libsycl' /tmp/uxl-sycl-transitive-libraries.txt

python3 - <<'PY'
import json
import os
from pathlib import Path
import subprocess

binary = '/tmp/uxl-sycl-transitive-public/transitive_probe'
environment = os.environ.copy()
selector = environment.get('UXL_SYCL_SELECTOR', '')
if selector:
    environment['ONEAPI_DEVICE_SELECTOR'] = selector


def expected_checksum(count, seed, scale):
    raw = sum((index * 13 + seed) % 101 for index in range(count))
    return raw * scale + count * 3


def run_case(count, seed, scale):
    output = subprocess.check_output(
        [binary, str(count), str(seed), str(scale)], text=True, env=environment
    )
    values = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
    assert values.get('status') == 'ok', values
    assert values.get('device'), values
    assert int(values['count']) == count, values
    assert int(values['seed']) == seed, values
    assert int(values['scale']) == scale, values
    assert int(values['checksum']) == expected_checksum(count, seed, scale), values
    assert int(values['expected']) == expected_checksum(count, seed, scale), values
    return values['device']


cases = ((1, 0, 1), (257, 29, 2), (8193, 61, 5), (16384, 7, 4))
devices = [run_case(*case) for case in cases]
unique_devices = sorted(set(devices))
reward = {
    'reward': 1.0,
    'hidden_cases': len(cases),
    'device_count': len(unique_devices),
}
Path('/logs/verifier/reward.json').write_text(
    json.dumps(reward, indent=2) + '\n', encoding='utf-8'
)
print(json.dumps({**reward, 'devices': unique_devices}, indent=2))
PY
