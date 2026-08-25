#!/bin/bash
set -euo pipefail

g++ -std=c++17 -O2 -fopenmp /app/weight_reorder.cpp -ldnnl -o /tmp/weight_reorder

DNNL_VERBOSE=1 /tmp/weight_reorder 4 32 5 4 3 > /tmp/public-trace.txt
python3 - /tmp/public-trace.txt 4 32 5 4 3 <<'PY'
from pathlib import Path
import sys


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


path, iterations, channels, height, width, seed = sys.argv[1:]
iterations, channels, height, width, seed = map(
    int, (iterations, channels, height, width, seed)
)
lines = Path(path).read_text(encoding="utf-8").splitlines()
verbose_prefixes = ("dnnl_verbose", "onednn_verbose")
verbose = [line.lower() for line in lines if line.lower().startswith(verbose_prefixes)]
reorders = [line for line in verbose if ",exec,cpu,reorder," in line]
convolutions = [line for line in verbose if ",exec,cpu,convolution," in line]
actual = [
    float(line)
    for line in lines
    if line.strip() and not line.lower().startswith(verbose_prefixes)
]

plane = height * width
size = channels * plane
src = [patterned(i, 17, seed * 13, 37, 18, 19.0) for i in range(size)]
weights = [
    patterned(i, 11, seed * 7, 31, 15, 23.0)
    for i in range(channels * channels)
]
bias = [patterned(i, 5, seed * 3, 17, 8, 29.0) for i in range(channels)]
expected = []
for spatial in range(plane):
    for oc in range(channels):
        total = bias[oc]
        for ic in range(channels):
            total += src[spatial * channels + ic] * weights[oc * channels + ic]
        expected.append(total)

assert len(actual) == len(expected), (len(actual), len(expected))
error = max(abs(left - right) for left, right in zip(actual, expected))
assert error < 2.0e-4, error
assert len(convolutions) == iterations, (len(convolutions), iterations)
assert len(reorders) == 1, (
    f"constant weights should be reordered once, observed {len(reorders)} executions"
)
print(f"public_max_abs_error={error:.8f}")
print(f"public_weight_reorders={len(reorders)}")
PY
