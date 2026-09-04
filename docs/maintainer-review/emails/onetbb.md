# oneTBB maintainer review email

**Subject:** Please review the first UXL agent skill for oneTBB

Hi oneTBB maintainers,

I built a first-pass UXL agent skill for oneTBB. It helps coding agents choose parallel patterns, set grain and partitioning deliberately, reason about flow-graph behavior, and diagnose races, cancellation, exceptions, and scheduler issues. The starting content came from current oneTBB documentation, examples, tests, and recurring failure patterns; [Harbor](https://github.com/harbor-framework/harbor) tasks make the evaluation inventory inspectable.

Start here:

- [oneTBB skill](https://github.com/uxlfoundation/skills/blob/main/skills/uxl-onetbb/SKILL.md)
- [Seven-slide maintainer briefing](https://uxlfoundation.github.io/skills/decks/uxl-onetbb-maintainer-briefing.pdf)
- [Dashboard detail](https://uxlfoundation.github.io/skills/skills/#uxl-onetbb)

The dashboard reports the health and coverage of the skill and its Harbor evaluations; it is not a score of oneTBB or its hardware support.

Could you please do two things?

1. Tell me the one most important correction to the skill's scope, terminology, or guidance.
2. Tell me whether a person or team can own or periodically review this small set of files.

UXL will continue to maintain the shared evaluator, dashboard, and runner contracts. If this is useful, we can improve the skill and its scenarios together.

Thanks,
[NAME]
