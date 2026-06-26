#!/usr/bin/env python3
"""Generate or check thin wrappers for popular agentic coding tools."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "CLAUDE.md": """# Claude Code Instructions

This repository builds UXL Foundation agent skills. Read `AGENTS.md` first; it is the canonical instruction file.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

Key rules:

- Treat each `skills/<skill-name>/SKILL.md` as a compact agent capability, not a documentation dump.
- Keep `skills.yaml`, `skill-cards/`, and per-skill `evals/evals.json` synchronized.
- Prefer official UXL project docs, examples, tests, benchmarks, and maintainer guidance.
- Verify current upstream support before answering questions about latest versions, hardware support, backend support, or release behavior.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` after changes.

Claude-specific note: keep this file concise. Put durable repo knowledge in `AGENTS.md`; put transient local notes in `CLAUDE.local.md` if needed and do not commit that file.
""",
    "GEMINI.md": """# Gemini CLI Instructions

This repository builds UXL Foundation agent skills. Use `AGENTS.md` as the source of truth for repo behavior.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

When working here:

- Keep skills concise and procedural.
- Keep detailed source material in `references/`.
- Keep `skills.yaml`, skill cards, and evals in sync.
- Use official UXL project sources for current API, backend, release, and hardware claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before finishing.

If you need more detail, read `AGENTS.md`, then the specific `skills/<skill-name>/SKILL.md` and `references/official-sources.md`.
""",
    ".github/copilot-instructions.md": """# GitHub Copilot Instructions

This repository maintains UXL Foundation agent skills. `AGENTS.md` is the canonical guidance file; use this file as the Copilot entry point and then consult `AGENTS.md` for details.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

Follow these rules:

- Keep `SKILL.md` files short, procedural, and triggerable.
- Put current source links in `references/official-sources.md`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Do not make compatibility or performance claims without official-source verification and validation evidence.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before proposing changes.

For UXL library details, prefer official project repositories and documentation over generic web results.
""",
    ".github/instructions/uxl-skills.instructions.md": """---
applyTo: "**"
---

When editing UXL skills catalog files:

- Update `skills.yaml` and the matching `skill-cards/<skill>.md` whenever a skill is added, renamed, or materially changed.
- Keep per-skill `SKILL.md` instructions concise; move detailed material to `references/`.
- Keep eval prompts realistic and runnable through `scripts/run_evals.py`.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
""",
    ".cursor/rules/uxl-skills.mdc": """---
description: UXL skills catalog authoring and validation rules
alwaysApply: true
---

This repository maintains UXL Foundation agent skills.

- Treat `AGENTS.md` as the canonical source of repository guidance.
- Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.
- Keep `SKILL.md` files concise and procedural.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Prefer official UXL project docs, tests, examples, benchmarks, and maintainer notes.
- Verify current upstream support before making release, backend, hardware, or compatibility claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before finishing.
""",
    ".continue/rules/uxl-skills.md": """---
name: UXL skills catalog
description: Repository rules for editing UXL Foundation agent skills
---

Use `AGENTS.md` as the canonical guidance for this repository.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

- Keep skills concise, procedural, and evidence-backed.
- Store detailed source material in `references/`.
- Keep `skills.yaml`, `skill-cards/`, and `evals/evals.json` synchronized.
- Verify current upstream support from official UXL sources before making compatibility claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
""",
    "CONVENTIONS.md": """# Aider Conventions

This repository maintains UXL Foundation agent skills. Load this file read-only for Aider sessions.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

- Use `AGENTS.md` as the source of truth for repository rules.
- Keep skill files concise and procedural.
- Keep deep documentation in `references/`, not in `SKILL.md`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Prefer official UXL project sources.
- Verify current release, backend, hardware, and compatibility claims before answering.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate` before finishing.
""",
    ".aider.conf.yml": "read: CONVENTIONS.md\n",
    ".windsurfrules": """This repository maintains UXL Foundation agent skills.

Use AGENTS.md as the canonical source of repo instructions.

Instruction precedence: when this wrapper and AGENTS.md differ, follow AGENTS.md.

Rules:
1. Keep SKILL.md files concise, procedural, and triggerable.
2. Put detailed source material in references/.
3. Keep skills.yaml, skill-cards/, and evals/evals.json synchronized.
4. Prefer official UXL project docs, tests, examples, benchmarks, and maintainer notes.
5. Verify current release, backend, hardware, and compatibility claims before answering.
6. Run python scripts/validate_catalog.py and python scripts/run_evals.py --validate before finishing.
""",
    ".clinerules/uxl-skills.md": """# UXL Skills Catalog Rules

Use `AGENTS.md` as the canonical source of repository instructions.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

- Keep `SKILL.md` files concise and procedural.
- Keep detailed references in `references/`.
- Keep `skills.yaml`, `skill-cards/`, and eval files synchronized.
- Prefer official UXL sources over generic web results.
- Verify current upstream support before making compatibility claims.
- Run `python scripts/validate_catalog.py` and `python scripts/run_evals.py --validate`.
""",
    "DEVIN.md": """# Devin Repo Notes

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
""",
    ".agents/skills/uxl-skills-catalog.md": """# UXL Skills Catalog

Use this repository skill when editing or reviewing UXL Foundation agent skills.

Follow `AGENTS.md`.

Instruction precedence: when this wrapper and `AGENTS.md` differ, follow `AGENTS.md`.

Checklist:

- Keep `SKILL.md` concise.
- Put detailed source material in `references/`.
- Keep `skills.yaml`, skill cards, and evals synchronized.
- Verify current UXL project docs before compatibility claims.
- Run `python scripts/validate_catalog.py`.
- Run `python scripts/run_evals.py --validate`.
""",
}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated wrappers differ from files on disk.")
    args = parser.parse_args(argv)

    mismatches: list[str] = []
    for rel, content in FILES.items():
        path = ROOT / rel
        if args.check:
            if not path.exists():
                mismatches.append(f"{rel}: missing")
            elif path.read_text(encoding="utf-8") != content:
                mismatches.append(f"{rel}: differs from generated content")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    if mismatches:
        print("Agent wrapper check failed:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"- {mismatch}", file=sys.stderr)
        return 1

    if args.check:
        print(f"Agent wrapper check passed: {len(FILES)} files.")
    else:
        print(f"Generated {len(FILES)} agent wrapper files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
