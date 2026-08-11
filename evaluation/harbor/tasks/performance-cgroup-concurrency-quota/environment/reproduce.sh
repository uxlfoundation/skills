#!/bin/bash
set -euo pipefail

g++ -std=c++17 -O2 -pthread /app/quota_parallel.cpp -ltbb -o /tmp/quota_parallel
/tmp/quota_parallel "${1:-/sys/fs/cgroup/cpu.max}"
