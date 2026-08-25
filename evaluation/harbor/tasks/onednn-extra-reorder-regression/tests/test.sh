#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/reproduce.sha256 || {
    echo "The public reproducer was modified; only /app/weight_reorder.cpp may change."
    exit 1
}

python3 - <<'PY'
from pathlib import Path

source = Path("/app/weight_reorder.cpp").read_text(encoding="utf-8")
required = (
    "convolution_forward::primitive_desc",
    "format_tag::any",
    "conv_pd.weights_desc()",
    "format_tag::nhwc",
    "format_tag::oihw",
    "DNNL_ARG_WEIGHTS",
    "reorder(",
)
for term in required:
    assert term in source, f"required optimized oneDNN path is missing: {term}"
PY

bash /app/reproduce.sh

g++ -std=c++17 -O2 -fopenmp /app/weight_reorder.cpp -ldnnl -o /tmp/weight_reorder

python3 - <<'PY'
import json
from pathlib import Path
import subprocess


def patterned(index, multiplier, seed_term, modulus, shift, divisor):
    return ((index * multiplier + seed_term) % modulus - shift) / divisor


def verify(iterations, channels, height, width, seed):
    completed = subprocess.run(
        [
            "/tmp/weight_reorder",
            str(iterations),
            str(channels),
            str(height),
            str(width),
            str(seed),
        ],
        env={**__import__("os").environ, "DNNL_VERBOSE": "1"},
        check=True,
        text=True,
        capture_output=True,
    )
    lines = completed.stdout.splitlines()
    verbose_prefixes = ("dnnl_verbose", "onednn_verbose")
    verbose = [
        line.lower() for line in lines if line.lower().startswith(verbose_prefixes)
    ]
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
    assert error < 2.0e-4, (iterations, channels, height, width, seed, error)
    assert len(convolutions) == iterations, (len(convolutions), iterations)
    assert len(reorders) == 1, (len(reorders), iterations)
    return error, len(reorders)


cases = (
    (2, 16, 3, 7, 11),
    (5, 32, 7, 3, 19),
    (3, 64, 2, 5, 23),
)
results = [verify(*case) for case in cases]
reward = {
    "reward": 1.0,
    "hidden_cases": len(cases),
    "max_abs_error": max(result[0] for result in results),
    "max_weight_reorders": max(result[1] for result in results),
}
Path("/logs/verifier/reward.json").write_text(
    json.dumps(reward, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(reward, indent=2))
PY
