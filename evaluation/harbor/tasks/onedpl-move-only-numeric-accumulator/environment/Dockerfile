FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++ \
        git \
        libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY onedpl-source.tar.gz /tmp/onedpl-source.tar.gz
RUN mkdir -p /app/oneDPL \
    && tar -xzf /tmp/onedpl-source.tar.gz -C /app/oneDPL \
    && rm /tmp/onedpl-source.tar.gz \
    && git init /app/oneDPL \
    && git -C /app/oneDPL config user.email evaluator@local \
    && git -C /app/oneDPL config user.name evaluator \
    && git -C /app/oneDPL add . \
    && git -C /app/oneDPL commit -m 'Pinned oneDPL pre-fix headers' >/dev/null

COPY reproduce.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/reproduce.cpp /app/reproduce.sh > /opt/reproducer.sha256

WORKDIR /app/oneDPL
