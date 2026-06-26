# Security Policy

This catalog contains instructions and helper scripts for coding agents.

## Reporting

Report suspected security issues through the UXL Foundation security process for the affected project when the issue is project-specific. For catalog-only issues, open a private report or contact the maintainers before public disclosure.

## Scope

Security-sensitive issues include:

- Scripts that execute unsafe commands.
- Prompt instructions that encourage leaking secrets or credentials.
- Skill guidance that bypasses project security policies.
- Supply-chain metadata that points to untrusted sources.

## Expectations

- Do not include secrets in skills, evals, examples, or test outputs.
- Keep helper scripts safe to run on developer workstations.
- Prefer read-only probes for environment discovery.
- Verify external links before publishing.
