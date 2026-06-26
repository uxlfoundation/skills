---
name: UXL skills catalog
description: Repository rules for editing UXL Foundation agent skills
---

Use `AGENTS.md` as the canonical guidance for this repository.

- Keep skills concise, procedural, and evidence-backed.
- Store detailed source material in `references/`.
- Keep `skills.yaml`, `skill-cards/`, and `evals/evals.json` synchronized.
- Verify current upstream support from official UXL sources before making compatibility claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
