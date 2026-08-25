#!/usr/bin/env bash
set -euo pipefail

export OPENBLASROOT=/opt/openblas
export TBBROOT=/opt/tbb

make -C /app/oneDAL -f makefile daal_c -j2 \
    COMPILER=gnu \
    PLAT=lnx32e \
    BACKEND_CONFIG=ref \
    REQCPU="sse2" \
    CORE.ALGORITHMS.CUSTOM="dtrees/forest" \
    >/tmp/onedal-build.log

if [[ "${1:-}" == "--build-only" ]]; then
    exit 0
fi

g++ -std=c++17 -O2 /app/reproduce.cpp \
    -I/app/oneDAL/__release_lnx_gnu/daal/latest/include \
    -L/app/oneDAL/__release_lnx_gnu/daal/latest/lib/intel64 \
    -Wl,-rpath,/app/oneDAL/__release_lnx_gnu/daal/latest/lib/intel64 \
    -lonedal_core -lonedal_thread -ltbb -ltbbmalloc -lpthread -ldl \
    -o /tmp/onedal-extra-trees-reproduce

/tmp/onedal-extra-trees-reproduce "${2:-10000}" "${3:-10}" "${4:-2468}" "${5:-0}"
