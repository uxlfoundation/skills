# Install and Use

This catalog has a public incubating release. Skills can be used directly from the checkout or copied into an agent-specific skills location.

For reproducible use, pin a tag or commit SHA. The initial incubating catalog release is tagged as `v0.1.0-incubating`.

## Codex

Use the repository instructions from `AGENTS.md`. For local skill testing, copy or symlink individual skill folders into your Codex skills directory, then invoke them by name, for example:

```text
Use $uxl-onemath to diagnose this oneMath CMake failure.
```

Run validation first:

```bash
python scripts/validate_catalog.py
python scripts/run_evals.py --validate
```

## Claude Code

Claude Code reads `CLAUDE.md`; this file points to `AGENTS.md`. Start Claude Code from the repository root so it loads the repository instructions.

Use explicit prompts while skills are incubating:

```text
Use the uxl-onemath skill at skills/uxl-onemath to choose a dispatch model for this code.
```

## GitHub Copilot

Copilot reads `.github/copilot-instructions.md` and path-specific instructions in `.github/instructions/`.

For cloud-agent work, include the repository and ask Copilot to inspect:

- `AGENTS.md`
- `skills.yaml`
- The relevant `skills/<skill-name>/SKILL.md`
- The relevant skill card

## Cursor, Continue, Cline, Windsurf, and Aider

The repository includes thin wrapper files for these tools. Keep `AGENTS.md` canonical and regenerate wrappers after changing repository-wide guidance:

```bash
python scripts/generate_agent_wrappers.py
```

## OpenHands-Style Agents

The repository includes `.agents/skills/uxl-skills-catalog.md` as a lightweight repository skill wrapper. The primary progressive-disclosure skills remain under `skills/<skill-name>/`.

## Publishing Path

1. Keep incubating work in this catalog.
2. Get project maintainer review for each library-specific skill.
3. Move the reviewed skill source of truth into the owning project repository.
4. Mirror the reviewed skill back into this catalog.
5. Publish tags and ask users to pin by tag or commit SHA.

See `docs/release-gates.md` before promoting any skill beyond `incubating` or `pilot`.
