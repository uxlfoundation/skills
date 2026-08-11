FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl g++ \
    && rm -rf /var/lib/apt/lists/*

ARG ONEMATH_SHA=be58ee06edbd9d98ec001c7ebcb8001b8b167a9a
RUN mkdir -p /app/vendor/oneMath \
    && curl --fail --location --silent --show-error \
        "https://github.com/uxlfoundation/oneMath/archive/${ONEMATH_SHA}.tar.gz" \
        | tar --extract --gzip --directory /app/vendor/oneMath --strip-components=1

WORKDIR /app
COPY smoke.cpp reproduce.sh /app/
COPY stubs /app/stubs
RUN chmod +x /app/reproduce.sh
