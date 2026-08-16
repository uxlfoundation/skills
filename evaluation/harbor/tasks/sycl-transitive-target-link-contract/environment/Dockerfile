FROM uxl-sycl-cpu:2026.1.1@sha256:90c67a1df80f57be32f0880ea5d638a75fd3df596ad2184e75d2a67c36513d79

ENV UXL_DPCPP_COMPILER=icpx
ENV UXL_SYCL_SELECTOR=opencl:cpu

WORKDIR /app
COPY CMakeLists.txt main.cpp pipeline.cpp pipeline.hpp sycl_stage.cpp sycl_stage.hpp reproduce.sh /app/
COPY cmake/UXLSYCL.cmake /app/cmake/UXLSYCL.cmake
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/main.cpp /app/pipeline.cpp /app/pipeline.hpp \
        /app/sycl_stage.cpp /app/sycl_stage.hpp /app/reproduce.sh \
        /app/cmake/UXLSYCL.cmake > /opt/sycl-transitive-protected.sha256
