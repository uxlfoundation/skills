#!/usr/bin/env bash
set -euo pipefail

g++ -std=c++17 -O2 -pthread \
    -I/app/oneDPL/include \
    /app/reproduce.cpp \
    -ltbb \
    -o /tmp/onedpl-move-only-public

/tmp/onedpl-move-only-public
