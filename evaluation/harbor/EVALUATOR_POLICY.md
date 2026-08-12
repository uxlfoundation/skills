# UXL skill evaluator policy

This policy defines what the Harbor portfolio proves about UXL agent skills. It separates skill evaluation from the owning projects' implementation and device qualification.

## Evaluation objective

A useful skill helps an agent reach a verified solution more reliably and efficiently. Skills should remain broadly hardware-agnostic. A task may still require specific hardware when the failure being triaged only reproduces there.

The evaluator measures:

- Correct API and workflow choices.
- Reproduction, investigation, repair, and verification behavior.
- Evidence quality and avoidance of unsupported claims.
- Reward, token usage, cost, and runtime for a verified solution.

The evaluator does not replace project CI for proving that every primitive, backend, driver, or device combination works or performs well.

## Task evidence levels

Every task declares its `reproduction`, `origin`, `workflow`, `hardware`, and `environment` in `suites.json`.

| Field | Values | Meaning |
| --- | --- | --- |
| `reproduction` | `live`, `fixture`, `review` | Whether the agent can reproduce and rerun the failure, only inspect supplied evidence, or review a choice or claim. |
| `origin` | `maintainer-incident`, `upstream-regression`, `constructed`, `unassigned`, `not-applicable` | Where the task scenario came from. |
| `workflow` | `reproduce`, `investigate`, `repair`, `verify` | Which stages the task actually exercises. |
| `hardware` | `none`, `generic-cpu`, `target-cpu`, `target-gpu`, `target-device`, `target-distributed` | The minimum hardware class needed for a valid run. |
| `environment` | Hosted, manual, or target environment | Where Harbor must dispatch the task. |

A task receives real end-to-end triage credit only when it:

1. Is implemented.
2. Reproduces the failure live in its declared environment.
3. Exercises reproduce, investigate, repair, and verify.
4. Is sourced from a maintainer incident or upstream regression.

Fixture and review tasks remain useful for reasoning, API selection, negative controls, and smoke coverage. They must not be reported as proof of real triage.

## Hardware policy

Use free hosted runners when they can reproduce the failure faithfully. Use target hardware when the failure depends on a device, backend, topology, driver, instruction set, or other property that the hosted runner does not provide.

The portfolio targets representative failures, not every task on every device. A hardware-specific task must identify the required hardware before implementation and must record the actual environment in its Harbor results. Skills do not need separate target-specific variants unless a future maintainer requirement demonstrates that the guidance itself must differ.

## Comparison and efficiency

Promotion evidence uses matched `no-skill`, `previous-skill`, and `candidate-skill` arms with the same task revision, agent, model, attempts, timeouts, and execution environment.

Quality is the gate. The primary efficiency metric is total token burn per verified success at the reward floor declared in `suites.json`. Cost per verified success and runtime are secondary operational metrics. Every comparison records:

- Uncached input tokens.
- Cached input tokens.
- Output tokens.
- Cost in USD.
- Runtime.
- Tool calls when the agent or Harbor exposes them.

Token or cost reductions do not compensate for lower verified success. Results should be compared within the same model and environment because tokenization, pricing, caching, and hardware can differ.

## Infrastructure failures

Runner, network, provisioning, and service failures are not task failures. Exclude and rerun them unchanged, preserve their logs, and report them separately. Do not rescore infrastructure errors as zero-reward skill attempts.

## Authoring and review checklist

Before implementing a planned task:

1. Confirm that the declared environment can reproduce the failure.
2. Source a maintainer incident or upstream regression for end-to-end triage credit.
3. Minimize the reproducer without removing the behavior under evaluation.
4. Define deterministic correctness checks before performance checks.
5. Make the verifier implementation-neutral and resistant to keyword-only answers.
6. Record environment and hardware provenance in the result.
7. Calibrate matched arms and report quality plus efficiency.

The generated `CAPABILITY_MATRIX.md` is the portfolio audit. It distinguishes live tasks from fixtures and reviews, identifies target-hardware requirements, and reports real end-to-end coverage separately.
