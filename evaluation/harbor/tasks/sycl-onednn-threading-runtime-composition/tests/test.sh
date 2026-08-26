#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
trap 'status=$?; if [[ $status -ne 0 ]]; then echo "verification failed; recorded zero reward"; fi; exit 0' EXIT

sha256sum --check --status /opt/protected.sha256 || {
  echo "Protected source or reproducer was modified."
  exit 1
}

grep -Eq 'set\(UXL_ONEDNN_RUNTIME[[:space:]]+"openmp"\)' /app/runtime.cmake || {
  echo "Select the coherent OpenMP oneDNN build in runtime.cmake."
  exit 1
}
if grep -Eqi 'ONEDNN_VERBOSE|DNNL_VERBOSE' /app/runtime.cmake; then
  echo "Verbose logging is not a repair."
  exit 1
fi

python3 - <<'PY'
from pathlib import Path

text = Path("/app/diagnosis.md").read_text(encoding="utf-8").lower()
groups = (
    ("execution", "runtime"),
    ("sycl",),
    ("tbb",),
    ("openmp",),
    ("ldd", "loader"),
    ("verbose",),
    ("perturb", "scheduling", "timing"),
    ("unverified", "not verified", "limited"),
)
for choices in groups:
    assert any(choice in text for choice in choices), choices
PY

UXL_REPEAT_COUNT=20 bash /app/reproduce.sh
grep -F '/opt/onednn/build-openmp/src/libdnnl.so.3' /app/loader-evidence.txt
grep -E 'libiomp5\.so' /app/loader-evidence.txt
if grep -Eq 'libtbb|libsycl' /app/loader-evidence.txt; then
  echo "The repaired executable still resolves the conflicting SYCL/TBB composition."
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path

reward = {
    "reward": 1.0,
    "hidden_repetitions": 20,
    "coherent_openmp_runtime": 1,
    "forbidden_runtime_libraries": 0,
}
Path("/logs/verifier/reward.json").write_text(
    json.dumps(reward, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(reward, indent=2))
PY
