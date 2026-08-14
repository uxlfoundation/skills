FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        libdnnl-dev=2.6.3-1 \
        python3 \
    && rm -rf /var/lib/apt/lists/*
ENV ONEDNN_MAX_CPU_ISA=AVX2

WORKDIR /app
COPY batched_matmul.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/reproduce.sh > /opt/reproduce.sha256
