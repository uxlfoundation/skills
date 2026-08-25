#!/bin/bash
set -euo pipefail
python - <<'PY'
from pathlib import Path

path = Path("/app/pipeline.py")
source = path.read_text(encoding="utf-8")
old = "training_table = np.asarray(feature_columns, dtype=np.float64)"
new = "training_table = np.asarray(feature_columns, dtype=np.float64).T"
if source.count(old) != 1:
    raise SystemExit("expected one training-table construction")
path.write_text(source.replace(old, new), encoding="utf-8")
PY
bash /tests/test.sh
