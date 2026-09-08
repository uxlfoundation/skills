import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
DECK_DIR = REPO_ROOT / "evaluation" / "dashboard" / "public" / "decks"
OVERVIEW_DECK = DECK_DIR / "uxl-skills-maintainer-overview.pptx"
SLIDE_PART = re.compile(r"ppt/slides/slide\d+\.xml$")
NOTES_PART = re.compile(r"ppt/notesSlides/notesSlide\d+\.xml$")


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

    def test_every_slide_has_descriptive_presenter_notes(self):
        decks = sorted(DECK_DIR.glob("*.pptx"))
        self.assertEqual(len(decks), 10)

        slide_total = 0
        note_total = 0
        for deck_path in decks:
            with self.subTest(deck=deck_path.name), ZipFile(deck_path) as deck:
                slide_parts = [name for name in deck.namelist() if SLIDE_PART.fullmatch(name)]
                note_parts = [name for name in deck.namelist() if NOTES_PART.fullmatch(name)]
                self.assertEqual(len(note_parts), len(slide_parts))
                slide_total += len(slide_parts)
                note_total += len(note_parts)

                for note_part in note_parts:
                    note_text = "".join(ET.fromstring(deck.read(note_part)).itertext())
                    self.assertIn("[Sources]", note_text)
                    self.assertIn("[/Sources]", note_text)
                    self.assertIn("Presenter guidance", note_text)
                    self.assertIn("Purpose:", note_text)
                    self.assertIn("Explain:", note_text)
                    self.assertIn("Emphasize:", note_text)
                    self.assertNotIn("Speaker cue:", note_text)

        self.assertEqual(slide_total, 73)
        self.assertEqual(note_total, 73)


if __name__ == "__main__":
    unittest.main()
