#!/bin/bash
set -euo pipefail

g++ -std=c++17 -O2 -fopenmp /app/residual_conv.cpp -ldnnl -o /tmp/residual_conv

/tmp/residual_conv 8 5 4 3 0.75 > /tmp/public-output.txt
python3 - /tmp/public-output.txt 8 5 4 3 0.75 <<'PY'
from pathlib import Path
import sys


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


path, channels, height, width, seed, residual_scale = sys.argv[1:]
channels, height, width, seed = map(int, (channels, height, width, seed))
residual_scale = float(residual_scale)
plane = height * width
size = channels * plane
src = [patterned(i, 17, seed * 13, 29, 14, 17.0) for i in range(size)]
weights = [patterned(i, 7, seed * 5, 19, 9, 23.0) for i in range(channels * channels)]
bias = [patterned(i, 5, seed * 3, 13, 6, 19.0) for i in range(channels)]
residual = [residual_scale * patterned(i, 11, seed * 3, 31, 15, 13.0) for i in range(size)]
expected = []
for oc in range(channels):
    for spatial in range(plane):
        total = bias[oc]
        for ic in range(channels):
            total += src[ic * plane + spatial] * weights[oc * channels + ic]
        index = oc * plane + spatial
        expected.append(max(0.0, total + residual[index]))

actual = [float(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
assert len(actual) == len(expected), (len(actual), len(expected))
error = max(abs(left - right) for left, right in zip(actual, expected))
print(f"public_max_abs_error={error:.8f}")
assert error < 1.0e-4, error
PY
