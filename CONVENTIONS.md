# Aider Conventions

This repository maintains UXL Foundation agent skills. Load this file read-only for Aider sessions.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

- Use `AGENTS.md` as the source of truth for repository rules.
- Keep skill files concise and procedural.
- Keep deep documentation in `references/`, not in `SKILL.md`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Prefer official UXL project sources.
- Verify current release, backend, hardware, and compatibility claims before answering.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before finishing.
