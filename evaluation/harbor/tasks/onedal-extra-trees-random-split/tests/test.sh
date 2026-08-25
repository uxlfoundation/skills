#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

if ! sha256sum --check --status /opt/reproducer.sha256; then
    echo "The public reproducer was modified."
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

source_file=/app/oneDAL/cpp/daal/src/algorithms/dtrees/forest/regression/df_regression_train_dense_default_impl.i
if ! grep -Fq 'decision_forest::training::random' /app/reproduce.cpp \
    || ! grep -Fq 'bootstrap = false' /app/reproduce.cpp \
    || ! grep -Fq 'leftWeights * left.var + rightWeights * right.var' "$source_file"; then
    echo "The repair must preserve random ExtraTrees training and use weight-scaled child impurity."
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

export OPENBLASROOT=/opt/openblas
export TBBROOT=/opt/tbb
if ! make -C /app/oneDAL -f makefile daal_c -j2 \
        COMPILER=gnu PLAT=lnx32e BACKEND_CONFIG=ref \
        REQCPU="sse2" CORE.ALGORITHMS.CUSTOM="dtrees/forest" \
        >/tmp/onedal-verifier-build.log; then
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

if ! g++ -std=c++17 -O2 /tests/reproduce.cpp \
        -I/app/oneDAL/__release_lnx_gnu/daal/latest/include \
        -L/app/oneDAL/__release_lnx_gnu/daal/latest/lib/intel64 \
        -Wl,-rpath,/app/oneDAL/__release_lnx_gnu/daal/latest/lib/intel64 \
        -lonedal_core -lonedal_thread -ltbb -ltbbmalloc -lpthread -ldl \
        -o /tmp/onedal-extra-trees-verify; then
    echo 0 > /logs/verifier/reward.txt
    cat /logs/verifier/reward.txt
    exit 0
fi

passed=1
for case in '10000 10 2468 0' '4096 7 9917 0' '2048 4 5309 0' '3072 6 7411 1'; do
    if ! timeout 120 /tmp/onedal-extra-trees-verify $case; then
        passed=0
    fi
done

echo "$passed" > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
