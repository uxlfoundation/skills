#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/residual_conv.cpp")
source = path.read_text(encoding="utf-8")
old_ops = """    conv_ops.append_eltwise(1.0f, algorithm::eltwise_relu, 0.0f, 0.0f);
    conv_ops.append_sum(1.0f);"""
new_ops = """    conv_ops.append_sum(1.0f);
    conv_ops.append_eltwise(1.0f, algorithm::eltwise_relu, 0.0f, 0.0f);"""
old_output = "    std::vector<float> output(output_size, 0.0f);"
new_output = "    std::vector<float> output = residual;"
if source.count(old_ops) != 1 or source.count(old_output) != 1:
    raise SystemExit("expected the two fusion defects exactly once")
path.write_text(
    source.replace(old_ops, new_ops).replace(old_output, new_output),
    encoding="utf-8",
)
PY

bash /tests/test.sh
