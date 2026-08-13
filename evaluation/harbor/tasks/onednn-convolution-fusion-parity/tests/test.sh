#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/residual_conv.cpp may change."
    exit 1
}

python3 - <<'PY'
from pathlib import Path

source = Path("/app/residual_conv.cpp").read_text(encoding="utf-8")
required = (
    "convolution_forward::primitive_desc",
    "format_tag::any",
    "append_sum",
    "append_eltwise",
    "conv_pd.dst_desc()",
    "reorder(user_dst, conv_dst)",
)
for term in required:
    assert term in source, f"required fused oneDNN path is missing: {term}"
assert source.index("append_sum") < source.index("append_eltwise"), (
    "the residual sum must precede ReLU for ReLU(conv+bias+residual)"
)
PY

bash /app/reproduce.sh

g++ -std=c++17 -O2 -fopenmp /app/residual_conv.cpp -ldnnl -o /tmp/residual_conv

python3 - <<'PY'
import json
from pathlib import Path
import subprocess


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


def verify(channels, height, width, seed, residual_scale):
    output = subprocess.check_output(
        [
            "/tmp/residual_conv",
            str(channels),
            str(height),
            str(width),
            str(seed),
            str(residual_scale),
        ],
        text=True,
    )
    actual = [float(line) for line in output.splitlines()]
    plane = height * width
    size = channels * plane
    src = [patterned(i, 17, seed * 13, 29, 14, 17.0) for i in range(size)]
    weights = [
        patterned(i, 7, seed * 5, 19, 9, 23.0)
        for i in range(channels * channels)
    ]
    bias = [
        patterned(i, 5, seed * 3, 13, 6, 19.0) for i in range(channels)
    ]
    residual = [
        residual_scale * patterned(i, 11, seed * 3, 31, 15, 13.0)
        for i in range(size)
    ]
    expected = []
    for oc in range(channels):
        for spatial in range(plane):
            total = bias[oc]
            for ic in range(channels):
                total += src[ic * plane + spatial] * weights[oc * channels + ic]
            index = oc * plane + spatial
            expected.append(max(0.0, total + residual[index]))
    assert len(actual) == len(expected)
    error = max(abs(left - right) for left, right in zip(actual, expected))
    assert error < 1.0e-4, (channels, height, width, seed, residual_scale, error)
    return error


cases = (
    (3, 2, 7, 11, 1.25),
    (8, 7, 3, 19, -0.5),
    (16, 4, 4, 5, 2.0),
    (5, 1, 9, 23, 0.125),
)
errors = [verify(*case) for case in cases]
reward = {"reward": 1.0, "hidden_cases": len(cases), "max_abs_error": max(errors)}
Path("/logs/verifier/reward.json").write_text(
    json.dumps(reward, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(reward, indent=2))
PY
