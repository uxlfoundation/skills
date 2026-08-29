#!/usr/bin/env python3
"""Compute the canonical UXL content digest for a directory tree."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path


def _git_root(directory: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip()).resolve()


def _git_directory_digest(root: Path, directory: Path) -> str:
    prefix = directory.relative_to(root).as_posix()
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            prefix,
        ],
        capture_output=True,
        check=True,
    )
    repo_paths = sorted(
        path for path in completed.stdout.decode("utf-8", errors="surrogateescape").split("\0") if path
    )
    lines = []
    for repo_path in repo_paths:
        absolute = root / Path(repo_path)
        if not absolute.is_file():
            continue
        hashed = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "hash-object",
                f"--path={repo_path}",
                "--",
                str(absolute),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        relative = absolute.relative_to(directory).as_posix()
        lines.append(f"{relative} {hashed.stdout.strip()}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def directory_digest(directory: Path) -> str:
    root = directory.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    repository = _git_root(root)
    if repository is not None and root.is_relative_to(repository):
        return _git_directory_digest(repository, root)
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
