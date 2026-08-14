FROM uxl-sycl-cpu:2026.1.1

ENV UXL_DPCPP_COMPILER=icpx
ENV UXL_SYCL_TARGET_FLAGS=-fsycl-targets=native_cpu
ENV UXL_SYCL_SELECTOR=native_cpu:cpu

WORKDIR /app
COPY CMakeLists.txt main.cpp sycl_kernel.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/main.cpp /app/sycl_kernel.cpp /app/reproduce.sh \
        > /opt/sycl-link-protected.sha256
