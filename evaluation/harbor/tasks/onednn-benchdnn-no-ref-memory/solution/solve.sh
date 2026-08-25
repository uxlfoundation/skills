#!/bin/bash
set -euo pipefail

source_file=/app/oneDNN/tests/benchdnn/conv/conv_dw_fusion.cpp
if ! grep -Fq 'has_bench_mode_modifier(mode_modifier_t::no_ref_memory)' "$source_file"; then
  sed -i '/res_t \*res, dir_t dir) {/a\    if (has_bench_mode_modifier(mode_modifier_t::no_ref_memory)) return OK;\n' "$source_file"
fi

bash /tests/test.sh
