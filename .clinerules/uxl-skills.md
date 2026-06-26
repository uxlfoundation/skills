# UXL Skills Catalog Rules

Use `AGENTS.md` as the canonical source of repository instructions.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

- Keep `SKILL.md` files concise and procedural.
- Keep detailed references in `references/`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Prefer official UXL sources over generic web results.
- Verify current upstream support before making compatibility claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
