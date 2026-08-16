FROM ubuntu:24.04@sha256:019e8eb29a85e74d64925745884f2ec79aa27e3feab36353d24656f4d6b89467 AS toolchain-base

ARG INTEL_DPCPP_VERSION=2026.1.1-325
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        cmake \
        git \
        gnupg \
        ninja-build \
        python3 \
        wget \
    && wget -qO- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
        | gpg --dearmor --output /usr/share/keyrings/oneapi-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" \
        > /etc/apt/sources.list.d/oneAPI.list \
    && apt-get update \
    && apt-get install --yes --no-install-recommends \
        "intel-oneapi-dpcpp-cpp-2026.1=${INTEL_DPCPP_VERSION}" \
    && rm -rf /var/lib/apt/lists/*

ENV ONEAPI_ROOT=/opt/intel/oneapi
ENV PATH=/opt/intel/oneapi/compiler/latest/bin:${PATH}
ENV LD_LIBRARY_PATH=/opt/intel/oneapi/compiler/latest/lib:/opt/intel/oneapi/compiler/latest/lib/x64:/opt/intel/oneapi/umf/latest/lib:/opt/intel/oneapi/tbb/latest/lib:/opt/intel/oneapi/tcm/latest/lib:/opt/intel/oneapi/common/latest/lib

FROM toolchain-base AS final

COPY smoke.cpp /opt/uxl-toolchain-smoke/smoke.cpp
RUN icpx --version \
    && icpx -std=c++17 -O0 -fsycl \
        /opt/uxl-toolchain-smoke/smoke.cpp \
        -o /opt/uxl-toolchain-smoke/smoke \
    && ONEAPI_DEVICE_SELECTOR=opencl:cpu sycl-ls \
    && ONEAPI_DEVICE_SELECTOR=opencl:cpu /opt/uxl-toolchain-smoke/smoke

WORKDIR /app
