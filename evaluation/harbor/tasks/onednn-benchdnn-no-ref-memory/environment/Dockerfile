FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ARG ONEDNN_BASE_REF=edc887bb71e405404dff49f8e29de7721f1e1720
ARG ONEDNN_FIX_REF=371711c6d09742d9a5a536c1ae54156ff33018bc

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential ca-certificates cmake git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git init oneDNN \
    && git -C oneDNN remote add origin https://github.com/uxlfoundation/oneDNN.git \
    && git -C oneDNN fetch --depth=2 origin refs/pull/5735/head \
    && test "$(git -C oneDNN rev-parse FETCH_HEAD)" = "$ONEDNN_FIX_REF" \
    && git -C oneDNN checkout --detach "$ONEDNN_BASE_REF" \
    && test "$(git -C oneDNN rev-parse HEAD)" = "$ONEDNN_BASE_REF"

RUN cmake -S /app/oneDNN -B /app/oneDNN/build \
        -DDNNL_BUILD_TESTS=ON \
        -DDNNL_BUILD_EXAMPLES=OFF \
        -DDNNL_BUILD_GRAPH=OFF \
        -DDNNL_CPU_RUNTIME=OMP \
        -DDNNL_GPU_RUNTIME=NONE \
        -DONEDNN_ENABLE_PRIMITIVE=CONVOLUTION \
        -DONEDNN_ENABLE_WORKLOAD=INFERENCE \
        -DONEDNN_ENABLE_GEMM_KERNELS_ISA=NONE \
        -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /app/oneDNN/build --target benchdnn --parallel 2

ENV ONEDNN_MAX_CPU_ISA=AVX2

COPY reproduce.sh /app/reproduce.sh
RUN chmod +x /app/reproduce.sh
