#!/bin/bash
set -euo pipefail

app_root="${APP_ROOT:-/app}"
build_root="${UXL_BUILD_ROOT:-/tmp/uxl-sycl-transitive-public}"
dpcpp_compiler="${UXL_DPCPP_COMPILER:-icpx}"
selector="${UXL_SYCL_SELECTOR:-}"
generator="${UXL_CMAKE_GENERATOR:-Ninja}"

case "${build_root}" in
    /tmp/uxl-sycl-transitive-*) ;;
    *) echo "refusing unsafe build directory: ${build_root}" >&2; exit 2 ;;
esac

rm -rf -- "${build_root}"
cmake -S "${app_root}" -B "${build_root}" -G "${generator}" \
    -DCMAKE_CXX_COMPILER="${dpcpp_compiler}"
cmake --build "${build_root}" --verbose

if [[ -n "${selector}" ]]; then
    ONEAPI_DEVICE_SELECTOR="${selector}" \
        "${build_root}/transitive_probe" 2048 11 3
else
    "${build_root}/transitive_probe" 2048 11 3
fi
