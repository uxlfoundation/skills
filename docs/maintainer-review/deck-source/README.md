# Maintainer deck source

These editable PPTX files preserve the UXL Foundation master, layouts, Arial/Lato typography, colors, logo, and 16:9 geometry used by the maintainer-outreach deck set.

`scripts/presentations/generate_maintainer_decks.mjs` imports these templates, applies the current concise content, replaces dashboard screenshots, and validates each final PPTX. `scripts/presentations/export_maintainer_deck_pdfs.ps1` exports matching PDFs through PowerPoint.

Published files live under `evaluation/dashboard/public/decks/` and are served by GitHub Pages at `https://uxlfoundation.github.io/skills/decks/`.
