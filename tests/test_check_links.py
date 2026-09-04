from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_links  # noqa: E402


class LinkCheckTests(unittest.TestCase):
    def test_skips_generated_workspace_directories(self) -> None:
        self.assertTrue(
            {"node_modules", "output", "tmp"}.issubset(check_links.SKIP_DIRECTORIES)
        )

    def test_skips_loopback_http_urls(self) -> None:
        self.assertFalse(check_links.should_check_external("http://127.0.0.1:8080"))
        self.assertFalse(check_links.should_check_external("http://localhost:8080/jobs"))
        self.assertFalse(check_links.should_check_external("http://[::1]:8080"))

    def test_checks_non_loopback_http_urls(self) -> None:
        self.assertTrue(check_links.should_check_external("https://github.com/example/project"))

    def test_validates_committed_pages_deck_without_network(self) -> None:
        handled, error = check_links.check_published_asset(
            "https://uxlfoundation.github.io/skills/decks/manifest.json"
        )
        self.assertTrue(handled)
        self.assertIsNone(error)

    def test_rejects_missing_pages_deck(self) -> None:
        handled, error = check_links.check_published_asset(
            "https://uxlfoundation.github.io/skills/decks/not-published.pdf"
        )
        self.assertTrue(handled)
        self.assertIn("missing committed Pages asset", error or "")

    def test_does_not_claim_unrelated_pages_url(self) -> None:
        handled, error = check_links.check_published_asset(
            "https://uxlfoundation.github.io/skills/methodology/"
        )
        self.assertFalse(handled)
        self.assertIsNone(error)

    def test_ignores_links_and_cpp_lambdas_inside_fenced_code(self) -> None:
        content = """\
[real](https://example.com/real)

```cpp
q.submit([&](sycl::handler& h) {});
// https://example.com/not-a-doc-link
```
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text(content, encoding="utf-8")
            self.assertEqual(
                check_links.extract_links(path), {"https://example.com/real"}
            )

    def test_ignores_bare_urls_inside_inline_code(self) -> None:
        content = "Use `https://example.com/not-a-link` and [this](guide.md)."
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text(content, encoding="utf-8")
            self.assertEqual(check_links.extract_links(path), {"guide.md"})


if __name__ == "__main__":
    unittest.main()
