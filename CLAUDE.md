# Claude Code Instructions

This repository builds UXL Foundation agent skills. Read `AGENTS.md` first; it is the canonical instruction file.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

Key rules:

- Treat each `skills/<skill-name>/SKILL.md` as a compact agent capability, not a documentation dump.
- Keep `skills.yaml`, `skill-cards/`, and per-skill `evals/evals.json` synchronized.
- Prefer official UXL project docs, examples, tests, benchmarks, and maintainer guidance.
- Verify current upstream support before answering questions about latest versions, hardware support, backend support, or release behavior.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` after changes.

Claude-specific note: keep this file concise. Put durable repo knowledge in `AGENTS.md`; put transient local notes in `CLAUDE.local.md` if needed and do not commit that file.
