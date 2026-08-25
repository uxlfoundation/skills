# UXL Library Teams Meeting Runbook — August 19, 2026

This runbook keeps the presentation and live demo on the current Windows workstation. Do not migrate, upgrade Docker, change Harbor, or clean the retained job directories before the meeting.

## Defensible milestone

- Eight skill suites cover six UXL libraries plus cross-project SYCL and performance workflows.
- The v1 portfolio defines 50 tasks; 38 are implemented and all 38 are classified.
- The repository validates 31 skill eval cases, 11 structured-answer checkers, and 56 unit tests.
- Harbor records the task, treatment, trajectory, artifacts, reward, token use, cost, and runtime for each trial.
- A self-hosted-runner contract and one specialized-hardware adapter are implemented, but a qualifying remote run has not yet completed.
- The current oneDNN comparison is a one-attempt development screen, not promotion evidence.

## Files and URLs

| Item | Location |
| --- | --- |
| Meeting deck | `output/uxl-working-group/UXL_Skills_Strategy_Library_Teams_2026-08-19.pptx` |
| Results dashboard | <http://127.0.0.1:8080> |
| Task dashboard | <http://127.0.0.1:8081> |
| Candidate job | <http://127.0.0.1:8080/jobs/milestone-onednn-layout-20260818-candidate> |
| No-skill job | <http://127.0.0.1:8080/jobs/milestone-onednn-layout-20260818-noskill> |
| Previous-skill job | <http://127.0.0.1:8080/jobs/milestone-onednn-layout-20260818-previous> |
| oneDNN task contract | <http://127.0.0.1:8081/task-definitions/onednn-framework-blocked-layout> |
| Evaluator quickstart | `docs/evaluator-quickstart.md` |
| Operator guide | `docs/evaluator-operator-guide.md` |
| Self-hosted runner policy | `docs/self-hosted-runners.md` |
| Private runner control template | `evaluation/runner-control-repo-template/` |

## Fifteen minutes before the meeting

1. Connect the workstation to power and start Docker Desktop.
2. From the repository root, refresh both dashboard indexes:

   ```powershell
   .\scripts\start_harbor_dashboards.ps1 -NoWsl -Restart
   ```

3. Confirm both services:

   ```powershell
   (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8080).StatusCode
   (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8081).StatusCode
   ```

4. Open the deck, candidate job, no-skill job, previous-skill job, and oneDNN task contract.
5. Keep the embedded screenshots on slides 6 and 7 as the fallback if browser sharing is slow.

## Suggested presentation sequence

1. **Slides 1–3 — purpose and architecture.** Skills should add project-specific leverage; Harbor holds the experiment constant and records evidence.
2. **Slides 4–5 — decision policy and coverage.** Quality gates efficiency. The portfolio makes ceiling, headroom, negative-control, and hardware gaps visible.
3. **Live results — candidate and no-skill jobs.** Use the task-row **Avg Reward**, not the job-header `answer_present` component. Explain that the candidate and previous skill scored 0.889 versus 0.556 without the skill, but no arm reached the 1.00 verified-success gate.
4. **Live task contract — `onednn-framework-blocked-layout`.** Show **Instruction**, then **Files**. Explain that task instructions and verifier source make the score inspectable.
5. **Slides 8–11 — runners, ownership, and decision.** Hosted runners remain the default; projects can plug in approved self-hosted runners when faithful reproduction requires specialized hardware. Close by choosing the repository ownership model.

## Claims to avoid

- Do not say that a specialized-hardware oracle has completed remotely; that qualification remains pending.
- Do not say a skill version is recommended; the current matched screen has one attempt per arm.
- Do not interpret lower token use as success when verified reward regresses.
- Do not describe the evaluator as a replacement for project CI or performance benchmarking.

## Library-team request

Ask each team for two concrete contributions:

1. Nominate one recurring maintainer failure that an agent should triage or repair more effectively with project-specific guidance.
2. When the failure depends on a device, backend, driver, topology, or instruction set, identify an existing controlled host that can run the reproducer.

Each specialized task declares its own runner requirements. The runner must record the actual environment, execute only reviewed evaluator revisions, and return the same Harbor job and provenance structure used by hosted runs.

## Likely questions

| Question | Short answer |
| --- | --- |
| Why not rely on model intelligence alone? | The baseline remains essential. A skill is justified only when it improves verified behavior or reduces tokens on an equally successful result. |
| Why Harbor? | It standardizes isolated trials, trajectories, artifacts, metrics, and result viewing while UXL teams define the skills, tasks, verifiers, and recommendation policy. |
| Why track tokens? | The primary efficiency measure is total tokens per verified success; quality is always the gate. |
| Why not require every target device? | Most skill guidance should be portable. Use target hardware only when faithful reproduction or verification depends on it. |
| Who owns hardware runners? | The library or infrastructure team that already owns the hardware; the evaluator consumes standardized artifacts from any approved execution system. |
| Can this run outside GitHub Actions? | Yes. The same Harbor commands can run over SSH, Jenkins, a lab scheduler, or another controlled CI system. |

## If the live demo fails

- Continue with the embedded dashboard screenshots on slides 6 and 7.
- Explain that every retained job is stored under `harbor-jobs/` and can be re-indexed locally.
- Do not troubleshoot Docker, install software, or rerun a model experiment during the meeting.
