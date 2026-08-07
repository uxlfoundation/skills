#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
python /tests/check_answer.py
