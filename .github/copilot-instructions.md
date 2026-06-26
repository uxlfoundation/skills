# GitHub Copilot Instructions

This repository maintains UXL Foundation agent skills. `AGENTS.md` is the canonical guidance file; use this file as the Copilot entry point and then consult `AGENTS.md` for details.

Follow these rules:

- Keep `SKILL.md` files short, procedural, and triggerable.
- Put current source links in `references/official-sources.md`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Do not make compatibility or performance claims without official-source verification and validation evidence.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before proposing changes.

For UXL library details, prefer official project repositories and documentation over generic web results.
