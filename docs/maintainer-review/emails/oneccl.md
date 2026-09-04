# oneCCL maintainer review email

**Subject:** Please review the first UXL agent skill for oneCCL

Hi oneCCL maintainers,

I built a first-pass UXL agent skill for oneCCL. It helps coding agents choose collective contracts, validate counts and datatypes, manage streams and events, reason about grouping and interoperability, and triage distributed hangs. The starting content came from current oneCCL documentation, examples, tests, and recurring failure patterns; [Harbor](https://github.com/harbor-framework/harbor) tasks make the evaluation inventory inspectable.

Start here:

- [oneCCL skill](https://github.com/uxlfoundation/skills/blob/main/skills/uxl-oneccl/SKILL.md)
- [Six-slide maintainer briefing](https://uxlfoundation.github.io/skills/decks/uxl-oneccl-maintainer-briefing.pdf)
- [Dashboard detail](https://uxlfoundation.github.io/skills/skills/#uxl-oneccl)

The dashboard reports the health and coverage of the skill and its Harbor evaluations; it is not a score of oneCCL or its hardware support.

Could you please do two things?

1. Tell me the one most important correction to the skill's scope, terminology, or guidance.
2. Tell me whether a person or team can own or periodically review this small set of files.

UXL will continue to maintain the shared evaluator, dashboard, and runner contracts. If this is useful, we can improve the skill and its scenarios together.

Thanks,
[NAME]
