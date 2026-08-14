#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/batched_matmul.cpp may change."
    exit 1
}

python3 - <<'PY'
from pathlib import Path

source = Path('/app/batched_matmul.cpp').read_text(encoding='utf-8')
required = (
    'dnnl::matmul::desc',
    'dnnl::matmul::primitive_desc',
    'DNNL_ARG_WEIGHTS',
    'weights_memory',
    '.execute(',
    'stream.wait()',
)
for term in required:
    assert term in source, f'required oneDNN matmul path is missing: {term}'
PY

bash /app/reproduce.sh
g++ -std=c++17 -O2 -fopenmp /app/batched_matmul.cpp -ldnnl -o /tmp/batched_matmul

python3 - <<'PY'
import json
from pathlib import Path
import subprocess


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


def verify(batch, m, k, n, seed):
    output = subprocess.check_output(
        ['/tmp/batched_matmul', str(batch), str(m), str(k), str(n), str(seed)],
        text=True,
    )
    actual = [float(line) for line in output.splitlines()]
    src = [patterned(i, 17, seed * 13, 29, 14, 17.0) for i in range(batch * m * k)]
    weights = [patterned(i, 7, seed * 5, 23, 11, 19.0) for i in range(batch * n * k)]
    expected = [
        sum(
            src[(b * m + row) * k + inner] * weights[(b * n + col) * k + inner]
            for inner in range(k)
        )
        for b in range(batch)
        for row in range(m)
        for col in range(n)
    ]
    assert len(actual) == len(expected), (len(actual), len(expected))
    error = max(abs(left - right) for left, right in zip(actual, expected))
    assert error < 1.0e-4, (batch, m, k, n, seed, error)
    return error


cases = (
    (1, 2, 3, 7, 5),
    (2, 5, 7, 3, 19),
    (3, 4, 5, 6, 23),
    (2, 1, 11, 4, 29),
)
errors = [verify(*case) for case in cases]
reward = {'reward': 1.0, 'hidden_cases': len(cases), 'max_abs_error': max(errors)}
Path('/logs/verifier/reward.json').write_text(
    json.dumps(reward, indent=2) + '\n', encoding='utf-8'
)
print(json.dumps(reward, indent=2))
PY
