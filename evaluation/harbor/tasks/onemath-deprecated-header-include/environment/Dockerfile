FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY smoke.cpp reproduce.sh /app/
COPY stubs /app/stubs
COPY vendor/oneMath/include /app/vendor/oneMath/include
RUN chmod +x /app/reproduce.sh
