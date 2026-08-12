#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier
reward=1
source_file=/app/oneDNN/tests/benchdnn/conv/conv_dw_fusion.cpp
bench=/app/oneDNN/build/tests/benchdnn/benchdnn
problems=(
  'ic128ih56oc128oh56kh1ph0nMobileNet_v1_fused_stride_2:conv2'
  'ic64ih28oc64oh28kh1ph0nVerifier_alt:conv2'
)
common=(
  --conv
  --summary=no-impl
  --dir=FWD_I
  --dt=s8:s8:s8
  --attr-post-ops=dw:k3s2p1
)

changed=$(git -C /app/oneDNN diff --name-only --diff-filter=ACDMRTUXB)
if [[ "$changed" != "tests/benchdnn/conv/conv_dw_fusion.cpp" ]]; then
  echo "unexpected changed files: ${changed:-none}"
  reward=0
fi

if ! cmake --build /app/oneDNN/build --target benchdnn --parallel 2; then
  echo "incremental benchdnn build failed"
  reward=0
fi

for problem_index in "${!problems[@]}"; do
  problem=${problems[$problem_index]}
  for mode in R S; do
    log="/tmp/benchdnn-${problem_index}-${mode}.log"
    if ! timeout 60 "$bench" "--mode=$mode" "${common[@]}" "$problem" >"$log" 2>&1; then
      echo "problem $problem_index mode $mode did not complete successfully"
      reward=0
    fi
    cat "$log"

    if ! grep -Eq 'tests:1 passed:1 .*failed:0' "$log" \
        || ! grep -Fq "$problem" "$log"; then
      echo "problem $problem_index mode $mode did not report one verified case"
      reward=0
    fi

    case "$mode" in
      R)
        grep -Fq '0:EXECUTED' "$log" || reward=0
        ;;
      S)
        grep -Fq 'perf,cpu,' "$log" || reward=0
        ;;
    esac
  done
done

if [[ ! -s "$source_file" ]]; then reward=0; fi
echo "$reward" > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
