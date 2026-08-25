FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        g++ \
        git \
        libopenblas-dev \
        libtbb-dev \
        make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY onedal-source.tar.gz /tmp/onedal-source.tar.gz
RUN mkdir -p /app/oneDAL \
    && tar -xzf /tmp/onedal-source.tar.gz -C /app/oneDAL \
    && rm /tmp/onedal-source.tar.gz \
    && mkdir -p /opt/openblas/lib /opt/tbb/lib \
    && ln -s /usr/include/x86_64-linux-gnu/openblas-pthread /opt/openblas/include \
    && ln -s /usr/lib/x86_64-linux-gnu/openblas-pthread/libopenblas.a /opt/openblas/lib/libopenblas.a \
    && ln -s /usr/include /opt/tbb/include \
    && ln -s /usr/lib/x86_64-linux-gnu/libtbb.so /opt/tbb/lib/libtbb.so \
    && ln -s /usr/lib/x86_64-linux-gnu/libtbbmalloc.so /opt/tbb/lib/libtbbmalloc.so \
    && sed -i '/__attribute__((__assume__(iStart < std::numeric_limits<std::ptrdiff_t>::max())));/d' \
       /app/oneDAL/cpp/daal/src/algorithms/dtrees/forest/regression/df_regression_train_dense_default_impl.i

RUN git init /app/oneDAL \
    && git -C /app/oneDAL config user.email evaluator@local \
    && git -C /app/oneDAL config user.name evaluator \
    && git -C /app/oneDAL add . \
    && git -C /app/oneDAL commit -m 'Pinned oneDAL 2026.1.0 task source' >/dev/null

COPY reproduce.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/reproduce.cpp /app/reproduce.sh > /opt/reproducer.sha256 \
    && /app/reproduce.sh --build-only

WORKDIR /app/oneDAL
