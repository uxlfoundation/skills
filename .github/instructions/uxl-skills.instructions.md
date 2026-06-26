---
applyTo: "**"
---

When editing UXL skills catalog files:

- Update `skills.yaml` and the matching `skill-cards/<skill>.md` whenever a skill is added, renamed, or materially changed.
- Keep per-skill `SKILL.md` instructions concise; move detailed material to `references/`.
- Keep eval prompts realistic and runnable through `scripts/run_evals.py`.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
