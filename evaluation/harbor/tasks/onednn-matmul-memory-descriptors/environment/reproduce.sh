#!/bin/bash
set -euo pipefail

g++ -std=c++17 -O2 -fopenmp /app/batched_matmul.cpp -ldnnl -o /tmp/batched_matmul
/tmp/batched_matmul 2 3 4 5 11 > /tmp/batched_matmul_public.txt

python3 - <<'PY'
from pathlib import Path

batch, m, k, n, seed = 2, 3, 4, 5, 11


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


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
actual = [float(line) for line in Path('/tmp/batched_matmul_public.txt').read_text().splitlines()]
assert len(actual) == len(expected), (len(actual), len(expected))
error = max(abs(left - right) for left, right in zip(actual, expected))
print(f'public max_abs_error={error:.9g}')
assert error < 1.0e-4, error
PY
