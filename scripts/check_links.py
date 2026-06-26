#!/usr/bin/env python3
"""Check local and external links in catalog Markdown and YAML files."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https?://[^\s)>\"]+")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SKIP_SCHEMES = {"mailto", "app", "plugin"}


def iter_files() -> list[Path]:
    patterns = ["*.md", "*.yaml", "*.yml"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(ROOT.rglob(pattern))
    return sorted(p for p in files if ".git" not in p.parts)


def clean_url(url: str) -> str:
    return url.rstrip(".,;")


def extract_links(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    links = {clean_url(match) for match in URL_RE.findall(text)}
    for match in MD_LINK_RE.findall(text):
        links.add(clean_url(match.strip()))
    return {link for link in links if link and not link.startswith("#")}


def check_local(path: Path, link: str) -> str | None:
    parsed = urllib.parse.urlparse(link)
    if parsed.scheme and parsed.scheme in SKIP_SCHEMES:
        return None
    if parsed.scheme in {"http", "https"}:
        return None
    if link.startswith("$") or link.startswith("<"):
        return None
    target = (path.parent / parsed.path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return f"{path}: local link escapes repository: {link}"
    if not target.exists():
        return f"{path}: broken local link: {link}"
    return None


def check_external(url: str, timeout: float) -> str | None:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "uxl-skills-link-checker/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status >= 400:
                return f"{url}: HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 429}:
            return None
        return f"{url}: HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - report all link failures
        return f"{url}: {exc}"
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--internal-only", action="store_true", help="Skip external HTTP checks.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Timeout per external link in seconds.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    external_links: set[str] = set()
    for path in iter_files():
        for link in extract_links(path):
            parsed = urllib.parse.urlparse(link)
            if parsed.scheme in {"http", "https"}:
                external_links.add(link)
            else:
                error = check_local(path, link)
                if error:
                    errors.append(error)

    if not args.internal_only:
        for url in sorted(external_links):
            error = check_external(url, args.timeout)
            if error:
                errors.append(error)

    if errors:
        print("Link check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    scope = "internal links" if args.internal_only else f"{len(external_links)} external links plus local links"
    print(f"Link check passed: {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
