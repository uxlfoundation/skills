FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY runtime_composition.h /app/runtime_composition.h
COPY runtime_composition.cpp /app/runtime_composition.cpp
