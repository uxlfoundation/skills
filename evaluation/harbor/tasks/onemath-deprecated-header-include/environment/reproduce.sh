#!/bin/bash
set -euo pipefail

g++ -std=c++17 -E \
  -I/app/stubs \
  -I/app/vendor/oneMath/include \
  /app/smoke.cpp \
  -o /tmp/onemath-mkl.i
