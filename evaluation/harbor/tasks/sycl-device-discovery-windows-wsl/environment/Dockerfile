FROM intel/oneapi:2026.1.0-devel-ubuntu24.04@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c

ENV LD_LIBRARY_PATH="/usr/lib/wsl/lib:${LD_LIBRARY_PATH}"
ENV ONEAPI_DEVICE_SELECTOR="level_zero:gpu"

WORKDIR /app
COPY sycl_probe.py gpu_smoke.cpp /app/
