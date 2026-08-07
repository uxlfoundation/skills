#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
python /tests/structured_answer.py --rubric /tests/rubric.json
