# Contributing

Thank you for improving the UXL agent skills catalog.

## Workflow

1. Read `AGENTS.md`.
2. Choose the smallest useful change.
3. Update the affected skill, its source ledger, evals, `skills.yaml`, and skill card together.
4. Run:

```powershell
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
```

5. If Codex skill tooling is available, run quick validation on changed skills.

## Skill Review

Project-specific skills should not be marked `reviewed` or `project-owned` until the owning UXL project maintainers have reviewed the skill content and source links.

## Evidence

For behavior changes, include at least one of:

- A new eval prompt.
- A source link from official docs, examples, tests, or benchmarks.
- A maintainer note.
- A validation log or benchmark result.

## Style

- Keep `SKILL.md` short.
- Put detailed material in `references/`.
- Keep scripts standard-library-first unless a dependency is clearly justified.
- Avoid claims about current support without verification.
