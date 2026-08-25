#!/usr/bin/env bash
set -euo pipefail

g++ -std=c++17 -O2 -Wall -Wextra -Werror \
    /app/reproduce.cpp \
    -o /tmp/onemath-storage-reproducer

/tmp/onemath-storage-reproducer
