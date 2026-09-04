# Maintainer review packets

These packets make the first project reviews small, explicit, and evidence-backed. They are drafts for outreach; their presence does not mean a maintainer has been contacted or has approved a skill.

Each reviewer is asked to check five things:

1. The skill triggers on appropriate project work and does not claim unsupported scope.
2. The procedures reflect current project guidance.
3. The limitations and routing advice are accurate.
4. The official-source ledger is sufficient and current.
5. The eval prompts and Harbor tasks represent realistic maintainer work.

Record the outcome in the relevant packet as `approved`, `changes requested`, or `ownership declined`. An approval should identify the reviewer, date, reviewed commit, and any required follow-up. Update the skill, source ledger, evals, card, and `skills.yaml` together when feedback changes scope or evidence.

Review packets:

- [oneCCL](uxl-oneccl.md)
- [oneDAL](uxl-onedal.md)
- [oneDNN](uxl-onednn.md)
- [oneDPL](uxl-onedpl.md)
- [oneMath](uxl-onemath.md)
- [oneTBB](uxl-onetbb.md)
- [Cross-project SYCL build/debug](uxl-sycl-build-debug.md)
- [Cross-project performance validation](uxl-performance-validation.md)

Use the [outreach guide](OUTREACH_GUIDE.md) for the short pitch, common questions, and review sequence. Use the [copy-ready issue text](ISSUE_TEMPLATE.md) when a project chooses GitHub for the review. These remain drafts until a human owner approves sending them.

Copy-ready project emails are under [`emails/`](emails/). Each asks for only two decisions: the most important correction and a named owner or periodic reviewer.

## Current maintainer decks

The editable PowerPoint and PDF versions are generated from the UXL-branded templates in [`deck-source/`](deck-source/). After the dashboard is deployed, the stable public files are:

- [Portfolio overview (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-skills-maintainer-overview.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-skills-maintainer-overview.pptx)
- [Specialized target onboarding (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-specialized-target-onboarding.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-specialized-target-onboarding.pptx)
- [oneDNN (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-onednn-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-onednn-maintainer-briefing.pptx)
- [oneMath (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-onemath-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-onemath-maintainer-briefing.pptx)
- [oneDAL (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-onedal-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-onedal-maintainer-briefing.pptx)
- [oneTBB (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-onetbb-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-onetbb-maintainer-briefing.pptx)
- [oneDPL (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-onedpl-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-onedpl-maintainer-briefing.pptx)
- [oneCCL (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-oneccl-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-oneccl-maintainer-briefing.pptx)
- [SYCL build/debug (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-sycl-build-debug-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-sycl-build-debug-maintainer-briefing.pptx)
- [Performance validation (PDF)](https://uxlfoundation.github.io/skills/decks/uxl-performance-validation-maintainer-briefing.pdf) · [PowerPoint](https://uxlfoundation.github.io/skills/decks/uxl-performance-validation-maintainer-briefing.pptx)

To rebuild them, run `scripts/presentations/generate_maintainer_decks.mjs` with the bundled presentation runtime, then `scripts/presentations/export_maintainer_deck_pdfs.ps1`. `scripts/presentations/package_maintainer_decks.ps1` creates a local shareable ZIP under `output/maintainer-outreach-current/`.
