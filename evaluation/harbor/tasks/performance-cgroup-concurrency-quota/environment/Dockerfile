FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends g++ libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY quota_parallel.cpp reproduce.sh /app/
RUN chmod +x /app/reproduce.sh
