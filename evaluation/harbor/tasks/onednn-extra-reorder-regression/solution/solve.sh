#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/weight_reorder.cpp")
source = path.read_text(encoding="utf-8")
old = """    for (int iteration = 0; iteration < iterations; ++iteration) {
        // Incorrect integration assumption: constant weights are repacked for each
        // request even though the primitive descriptor and user weights are stable.
        auto conv_weights = memory(conv_pd.weights_desc(), eng);
        reorder(user_weights, conv_weights).execute(
                strm, user_weights, conv_weights);
        conv.execute(strm,
"""
new = """    auto conv_weights = memory(conv_pd.weights_desc(), eng);
    reorder(user_weights, conv_weights).execute(strm, user_weights, conv_weights);
    strm.wait();

    for (int iteration = 0; iteration < iterations; ++iteration) {
        conv.execute(strm,
"""
if source.count(old) != 1:
    raise SystemExit("expected repeated weight reorder block exactly once")
path.write_text(source.replace(old, new), encoding="utf-8")
PY

bash /tests/test.sh
