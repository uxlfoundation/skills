#!/usr/bin/env python3
"""Check local and external links in catalog Markdown and YAML files."""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https?://[^\s)>\"]+")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SKIP_SCHEMES = {"mailto", "app", "plugin"}
TRANSIENT_NETWORK_ERRORS = (
    "network is unreachable",
    "temporarily unavailable",
    "temporary failure",
    "timed out",
    "connection reset",
    "remote end closed connection",
    "name or service not known",
    "errno 101",
    "errno 110",
)


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


def is_transient_network_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__}: {exc}".lower()
    reason = getattr(exc, "reason", None)
    if reason is not None:
        text = f"{text} {type(reason).__name__}: {reason}".lower()
    return any(fragment in text for fragment in TRANSIENT_NETWORK_ERRORS)


def check_external(url: str, timeout: float, retries: int) -> tuple[str, str] | None:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "uxl-skills-link-checker/1.0"},
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status >= 400:
                    return ("error", f"{url}: HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403, 429}:
                return None
            return ("error", f"{url}: HTTP {exc.code}")
        except Exception as exc:  # noqa: BLE001 - classify and report all link failures
            if attempt < retries and is_transient_network_error(exc):
                time.sleep(1)
                continue
            kind = "transient" if is_transient_network_error(exc) else "error"
            return (kind, f"{url}: {exc}")
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--internal-only", action="store_true", help="Skip external HTTP checks.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Timeout per external link in seconds.")
    parser.add_argument("--retries", type=int, default=0, help="Retries for transient external network failures.")
    parser.add_argument(
        "--warn-transient-network-errors",
        action="store_true",
        help="Report transient external network failures as warnings instead of errors.",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []
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
            issue = check_external(url, args.timeout, args.retries)
            if issue:
                kind, message = issue
                if kind == "transient" and args.warn_transient_network_errors:
                    warnings.append(message)
                else:
                    errors.append(message)

    if errors:
        print("Link check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if warnings:
        print("Link check warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)

    scope = "internal links" if args.internal_only else f"{len(external_links)} external links plus local links"
    print(f"Link check passed: {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
