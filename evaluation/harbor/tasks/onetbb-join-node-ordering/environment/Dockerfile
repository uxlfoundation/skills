FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY join_pipeline.h join_pipeline.cpp /app/
