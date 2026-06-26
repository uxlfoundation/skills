# Release and Promotion Policy

This repository is already public and released. The policy below is not a blocker for the current `v0.1.0-incubating` release; it governs future catalog releases and promotion of individual skills.

## Catalog Releases

A catalog release publishes a pin-able state of this repository. An incubating catalog release makes the skills discoverable and usable while keeping their review status explicit. It does not mean every skill is maintainer-reviewed or ready to become the source of truth in its owning project repository.

Required for future catalog releases:

1. All skills have explicit status values in `skills.yaml`.
2. No skill is marked `reviewed` or `project-owned` without maintainer evidence.
3. Skill cards record owner, source location, limitations, and validation evidence.
4. Catalog, eval, wrapper drift, agnix, and link checks pass.
5. Helper scripts have smoke-test coverage in CI.
6. A release ledger entry records what was shipped and what remains deferred.
7. A tag or commit SHA is available for pinning.

## Skill Promotion

A skill promotion moves one or more skills beyond incubation. These criteria apply before setting a skill status to `reviewed` or `project-owned`.

Required for promotion:

1. Owning project maintainer review is recorded.
2. Current official sources were rechecked after maintainer feedback.
3. At least three realistic eval prompts exist for the skill.
4. With-skill and without-skill forward-test outputs are saved or summarized.
5. The skill card records owner, sources, limitations, risks, forward-test evidence, and remaining gaps.
6. The catalog validation suite passes.
7. For `project-owned`, the owning project repository is the source of truth and this catalog is only a mirror.

## Current Status

The public repository is released as an incubating catalog. The skills remain `incubating` or `pilot` until the skill promotion criteria are satisfied.

See the release ledger in `docs/releases/`.
