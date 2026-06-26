# Devin Repo Notes

This repository maintains UXL Foundation agent skills. Devin and similar autonomous agents use `AGENTS.md` as the source of truth.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

Start with:

```bash
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
```

Before changing a skill, inspect:

- `skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/references/official-sources.md`
- `skills/<skill-name>/evals/evals.json`
- `skill-cards/<skill-name>.md`
- `skills.yaml`

Mark a skill reviewed or project-owned only after maintainer evidence is recorded.
