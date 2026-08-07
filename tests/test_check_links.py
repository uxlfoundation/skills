from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_links  # noqa: E402


class LinkCheckTests(unittest.TestCase):
    def test_skips_loopback_http_urls(self) -> None:
        self.assertFalse(check_links.should_check_external("http://127.0.0.1:8080"))
        self.assertFalse(check_links.should_check_external("http://localhost:8080/jobs"))
        self.assertFalse(check_links.should_check_external("http://[::1]:8080"))

    def test_checks_non_loopback_http_urls(self) -> None:
        self.assertTrue(check_links.should_check_external("https://github.com/example/project"))


if __name__ == "__main__":
    unittest.main()
