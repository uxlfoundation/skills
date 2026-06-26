# 2026-06-26 Initial Public Catalog Release

Release type: incubating catalog release

Release tag: `v0.1.0-incubating`

## Scope

This release publishes the central UXL agent skills catalog with:

- Six UXL oneAPI library skills: oneDNN, oneMath, oneDAL, oneTBB, oneDPL, and oneCCL.
- Two cross-project skills: SYCL build/debug and performance validation.
- Agent wrapper files for Codex/AGENTS-compatible agents, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Continue, Aider, Windsurf, Cline, Devin-style workflows, and OpenHands-style repository skills.
- Catalog, eval, link, wrapper-drift, agnix, and helper-script validation in CI.

## Gate Results

Satisfied for this incubating catalog release:

- All skills have explicit status values.
- No skill is marked `reviewed` or `project-owned`.
- Skill cards exist for every skill and record limitations.
- Every skill has at least three eval prompts.
- Catalog, eval, wrapper, link, agnix, and helper-script smoke checks passed locally before release.
- CI runs the same validation suite on push and pull request.

Deferred until reviewed skill releases:

- Owning project maintainer review.
- With-skill and without-skill forward-test evidence.
- Moving library-specific skill source of truth into the owning project repositories.

## Notes

`uxl-onemath` is the first pilot skill and has deeper source references. All other skills remain incubating.
