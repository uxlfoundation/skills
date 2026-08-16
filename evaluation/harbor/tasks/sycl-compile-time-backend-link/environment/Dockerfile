FROM uxl-sycl-cpu:2026.1.1@sha256:90c67a1df80f57be32f0880ea5d638a75fd3df596ad2184e75d2a67c36513d79

ENV UXL_DPCPP_COMPILER=icpx
ENV UXL_SYCL_TARGET_FLAGS=""
ENV UXL_SYCL_SELECTOR=opencl:cpu

WORKDIR /app
COPY CMakeLists.txt main.cpp sycl_kernel.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/main.cpp /app/sycl_kernel.cpp /app/reproduce.sh \
        > /opt/sycl-link-protected.sha256
