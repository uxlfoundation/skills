#!/usr/bin/env python3
"""Approve a SYCL observation. This starter checks too little evidence."""

import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    contract = json.load(source)
with open(sys.argv[2], encoding="utf-8") as source:
    observation = json.load(source)

reasons = []
if observation["device"]["type"].lower() != contract["device_type"].lower():
    reasons.append("device-type-mismatch")
if observation["kernel"]["result_sha256"] != contract["result_sha256"]:
    reasons.append("result-mismatch")

print(
    json.dumps(
        {
            "schema_version": "1.0",
            "status": "accepted" if not reasons else "rejected",
            "reasons": reasons,
        }
    )
)
