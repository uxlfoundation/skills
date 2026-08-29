#!/usr/bin/env python3
"""Compute the canonical UXL content digest for a directory tree."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def directory_digest(directory: Path) -> str:
    root = directory.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    lines = []
    for path in sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{relative} {digest}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        print(directory_digest(args.directory))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
