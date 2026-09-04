# oneMath maintainer review email

**Subject:** Please review the first UXL agent skill for oneMath

Hi oneMath maintainers,

I built a first-pass UXL agent skill for oneMath. It helps coding agents choose APIs and computation modes, diagnose build and runtime linkage, respect mathematical storage and workspace contracts, and validate numerical results. The starting content came from current oneMath documentation, examples, tests, and recurring failure patterns; [Harbor](https://github.com/harbor-framework/harbor) tasks make the evaluation inventory inspectable.

Start here:

- [oneMath skill](https://github.com/uxlfoundation/skills/blob/main/skills/uxl-onemath/SKILL.md)
- [Six-slide maintainer briefing](https://uxlfoundation.github.io/skills/decks/uxl-onemath-maintainer-briefing.pdf)
- [Dashboard detail](https://uxlfoundation.github.io/skills/skills/#uxl-onemath)

The dashboard reports the health and coverage of the skill and its Harbor evaluations; it is not a score of oneMath or its hardware support.

Could you please do two things?

1. Tell me the one most important correction to the skill's scope, terminology, or guidance.
2. Tell me whether a person or team can own or periodically review this small set of files.

UXL will continue to maintain the shared evaluator, dashboard, and runner contracts. If this is useful, we can improve the skill and its scenarios together.

Thanks,
[NAME]
