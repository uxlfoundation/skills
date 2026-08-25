FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ARG ONEDPL_REF=7be7189277bf0d0992806edc080b153046e5c2ac

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        g++ \
        git \
        libtbb-dev \
        python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git init /opt/onedpl \
    && git -C /opt/onedpl remote add origin https://github.com/uxlfoundation/oneDPL.git \
    && git -C /opt/onedpl fetch --depth 1 origin "${ONEDPL_REF}" \
    && test "$(git -C /opt/onedpl rev-parse FETCH_HEAD)" = "${ONEDPL_REF}" \
    && git -C /opt/onedpl checkout --detach FETCH_HEAD \
    && rm -rf /opt/onedpl/.git

WORKDIR /app
COPY order_events.cpp reproduce.sh /app/
RUN sha256sum /app/reproduce.sh > /opt/reproduce.sha256
