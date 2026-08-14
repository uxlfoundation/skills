FROM debian:bookworm-slim@sha256:abd67ffcfa541b485a3dff59865ab629aa048a6c613e639d36e7456b0b229241

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ git \
    && rm -rf /var/lib/apt/lists/*

COPY immutable /app/immutable
COPY source /app/oneMath
COPY reproduce.cpp reproduce.sh /app/

RUN chmod +x /app/reproduce.sh \
    && sha256sum /app/reproduce.cpp /app/reproduce.sh /app/immutable/fixture_support.hpp \
        > /opt/reproducer.sha256 \
    && git init /app/oneMath \
    && git -C /app/oneMath config user.email evaluator@local \
    && git -C /app/oneMath config user.name evaluator \
    && git -C /app/oneMath add . \
    && git -C /app/oneMath commit -m 'Pinned oneMath pre-fix fixture excerpt' >/dev/null

WORKDIR /app/oneMath
