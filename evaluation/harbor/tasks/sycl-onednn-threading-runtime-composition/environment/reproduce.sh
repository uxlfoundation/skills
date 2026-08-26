#!/bin/bash
set -uo pipefail

build_dir=/tmp/uxl-onednn-runtime-build
rm -rf "$build_dir"
cmake -S /app -B "$build_dir" -DCMAKE_CXX_COMPILER=icpx -DCMAKE_BUILD_TYPE=Release || exit 1
cmake --build "$build_dir" --parallel 2 || exit 1

binary="$build_dir/cpu_rnn_inference_int8"
if grep -Eq 'set\(UXL_ONEDNN_RUNTIME[[:space:]]+"openmp"\)' /app/runtime.cmake; then
  selected_build=/opt/onednn/build-openmp
else
  selected_build=/opt/onednn/build-sycl
fi
export LD_LIBRARY_PATH="$selected_build/src:${LD_LIBRARY_PATH:-}"
ldd "$binary" | tee /app/loader-evidence.txt

unset ONEDNN_VERBOSE DNNL_VERBOSE
repeat_count="${UXL_REPEAT_COUNT:-12}"
failures=0
for attempt in $(seq 1 "$repeat_count"); do
  "$binary" >/tmp/uxl-onednn-run.out 2>/tmp/uxl-onednn-run.err
  status=$?
  if [[ $status -ne 0 ]]; then
    failures=$((failures + 1))
    printf 'attempt=%s status=%s\n' "$attempt" "$status"
  elif ! grep -q 'Example passed' /tmp/uxl-onednn-run.out; then
    failures=$((failures + 1))
    printf 'attempt=%s status=missing-success-marker\n' "$attempt"
  fi
done

printf 'runs=%s failures=%s\n' "$repeat_count" "$failures"
[[ $failures -eq 0 ]]
