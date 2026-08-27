FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++ \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY oneccl-source /app/oneCCL
RUN git init /app/oneCCL \
    && git -C /app/oneCCL config user.email evaluator@local \
    && git -C /app/oneCCL config user.name evaluator \
    && git -C /app/oneCCL add . \
    && git -C /app/oneCCL commit -m 'Pinned oneCCL issue 174 fixture' >/dev/null

COPY reproduce.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum \
        /app/reproduce.cpp \
        /app/reproduce.sh \
        /app/oneCCL/include/oneccl_incident/alltoallv_model.hpp \
        > /opt/reproducer.sha256

WORKDIR /app/oneCCL
