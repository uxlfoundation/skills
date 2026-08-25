#!/bin/bash
set -uo pipefail

bench=/app/oneDNN/build/tests/benchdnn/benchdnn
problem='ic128ih56oc128oh56kh1ph0nMobileNet_v1_fused_stride_2:conv2'
common=(
  --conv
  --summary=no-impl
  --dir=FWD_I
  --dt=s8:s8:s8
  --attr-post-ops=dw:k3s2p1
  "$problem"
)

status=0
for mode in R S; do
  echo "===== mode=$mode ====="
  output=$(timeout 45 "$bench" "--mode=$mode" "${common[@]}" 2>&1)
  rc=$?
  printf '%s\n' "$output"
  echo "mode=$mode exit=$rc"
  if [[ "$rc" -ne 0 ]]; then status=1; fi
done

exit "$status"
