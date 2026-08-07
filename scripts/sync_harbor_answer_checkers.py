#!/usr/bin/env python3
"""Sync the shared structured-answer checker into Harbor task test directories."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evaluation" / "harbor" / "shared" / "structured_answer.py"
TASKS = ROOT / "evaluation" / "harbor" / "tasks"


def targets() -> list[Path]:
    return sorted(
        rubric.parent / "structured_answer.py"
        for rubric in TASKS.glob("*/tests/rubric.json")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = SOURCE.read_text(encoding="utf-8")
    stale: list[Path] = []
    found = targets()
    for target in found:
        if target.exists() and target.read_text(encoding="utf-8") == expected:
            continue
        if args.check:
            stale.append(target)
        else:
            target.write_text(expected, encoding="utf-8")
            print(f"Updated {target.relative_to(ROOT)}")
    if stale:
        print("Structured-answer checkers are stale:")
        for target in stale:
            print(f"- {target.relative_to(ROOT)}")
        return 1
    if args.check:
        print(f"Structured-answer checkers are current: {len(found)} tasks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
