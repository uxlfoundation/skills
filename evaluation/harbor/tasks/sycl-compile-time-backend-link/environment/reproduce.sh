#!/bin/bash
set -euo pipefail

app_root="${APP_ROOT:-/app}"
build_root="${UXL_BUILD_ROOT:-/tmp/uxl-sycl-link-public}"
dpcpp_compiler="${UXL_DPCPP_COMPILER:-icpx}"
target_flags="${UXL_SYCL_TARGET_FLAGS:-}"
selector="${UXL_SYCL_SELECTOR:-}"
generator="${UXL_CMAKE_GENERATOR:-Ninja}"

case "${build_root}" in
    /tmp/uxl-sycl-link-*) ;;
    *) echo "refusing unsafe build directory: ${build_root}" >&2; exit 2 ;;
esac

rm -rf -- "${build_root}"
cmake -S "${app_root}" -B "${build_root}" -G "${generator}" \
    -DCMAKE_CXX_COMPILER=g++ \
    -DDPCPP_COMPILER="${dpcpp_compiler}" \
    -DSYCL_TARGET_FLAGS="${target_flags}"
cmake --build "${build_root}" --verbose

if [[ -n "${selector}" ]]; then
    ONEAPI_DEVICE_SELECTOR="${selector}" "${build_root}/sycl_probe" 4096 17
else
    "${build_root}/sycl_probe" 4096 17
fi
