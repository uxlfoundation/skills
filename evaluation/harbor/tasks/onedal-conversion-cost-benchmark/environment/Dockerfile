FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN python -m pip install --no-cache-dir \
        packaging==25.0 \
        scikit-learn-intelex==2026.1.0

WORKDIR /app
COPY benchmark.py reproduce.py /app/
RUN sha256sum /app/reproduce.py > /opt/reproduce.sha256
