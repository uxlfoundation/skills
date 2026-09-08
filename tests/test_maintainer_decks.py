import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
OVERVIEW_DECK = REPO_ROOT / "evaluation" / "dashboard" / "public" / "decks" / "uxl-skills-maintainer-overview.pptx"
SLIDE_PART = re.compile(r"ppt/slides/slide\d+\.xml$")


class MaintainerDeckTests(unittest.TestCase):
    def test_overview_opens_with_current_state(self):
        with ZipFile(OVERVIEW_DECK) as deck:
            slide_parts = [name for name in deck.namelist() if SLIDE_PART.fullmatch(name)]
            visible_text = "\n".join(
                "".join(ET.fromstring(deck.read(name)).itertext())
                for name in slide_parts
            )

        self.assertEqual(len(slide_parts), 13)
        self.assertIn("What exists today", visible_text)
        self.assertNotIn("Why project maintainers should care", visible_text)


if __name__ == "__main__":
    unittest.main()
