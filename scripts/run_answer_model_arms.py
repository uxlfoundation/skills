#!/usr/bin/env python3
"""Run real model or agent commands for baseline and skill-explicit answer arms."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from run_evals import EvalCase, load_evals


ROOT = Path(__file__).resolve().parents[1]


def parse_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    selected: set[str] = set()
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                selected.add(item)
    return selected or None


def baseline_prompt(case: EvalCase) -> str:
    prefix = f"Use ${case.skill} to "
    if case.prompt.startswith(prefix):
        remainder = case.prompt[len(prefix) :]
        return remainder[:1].upper() + remainder[1:]
    return case.prompt.replace(f"${case.skill}", case.skill)


def command_context(case: EvalCase, arm: str, prompt: str, prompt_file: Path, output_file: Path) -> dict[str, str]:
    return {
        "arm": arm,
        "skill": case.skill,
        "eval_id": case.eval_id,
        "prompt_file": str(prompt_file),
        "output_file": str(output_file),
        "skill_path": str(ROOT / "skills" / case.skill),
        "repo_root": str(ROOT),
        "prompt": prompt,
    }


def render_command(command_template: str, context: dict[str, str]) -> str:
    command = command_template
    for key, value in context.items():
        command = command.replace("{" + key + "}", value)
    return command


def run_command(command_template: str, case: EvalCase, arm: str, prompt: str, output_file: Path, timeout: int) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file = output_file.with_suffix(".prompt.md")
    prompt_file.write_text(prompt, encoding="utf-8")
    context = command_context(case, arm, prompt, prompt_file, output_file)
    command = render_command(command_template, context)
    env = os.environ.copy()
    env.update(
        {
            "UXL_EVAL_ARM": arm,
            "UXL_EVAL_SKILL": case.skill,
            "UXL_EVAL_ID": case.eval_id,
            "UXL_EVAL_PROMPT": prompt,
            "UXL_EVAL_PROMPT_FILE": str(prompt_file),
            "UXL_EVAL_OUTPUT_FILE": str(output_file),
            "UXL_SKILL_PATH": str(ROOT / "skills" / case.skill),
            "UXL_REPO_ROOT": str(ROOT),
        }
    )
    completed = subprocess.run(
        command,
        shell=True,
        cwd=ROOT,
        env=env,
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise RuntimeError(f"{arm} command failed for {case.skill}/{case.eval_id}: exit {completed.returncode}")

    if output_file.exists() and output_file.read_text(encoding="utf-8").strip():
        return
    output_file.write_text(completed.stdout, encoding="utf-8")


def selected_cases(skill_filter: set[str] | None, eval_filter: set[str] | None) -> list[EvalCase]:
    cases, errors = load_evals()
    if errors:
        raise RuntimeError("\n".join(errors))
    if skill_filter is not None:
        cases = [case for case in cases if case.skill in skill_filter]
    if eval_filter is not None:
        cases = [case for case in cases if case.eval_id in eval_filter]
    if not cases:
        raise RuntimeError("No eval cases selected.")
    return cases


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-command", required=True, help="Command template for the no-skill baseline arm.")
    parser.add_argument("--skill-command", required=True, help="Command template for the skill-explicit arm.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory that will receive baseline/ and skill-explicit/.")
    parser.add_argument("--skill", action="append", help="Skill filter. May be repeated or comma-separated.")
    parser.add_argument("--eval", action="append", help="Eval id filter. May be repeated or comma-separated.")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Per-command timeout.")
    parser.add_argument("--same-prompt", action="store_true", help="Send the skill prompt to both arms.")
    parser.add_argument("--dry-run", action="store_true", help="Print selected cases without invoking commands.")
    args = parser.parse_args(argv)

    try:
        cases = selected_cases(parse_filter(args.skill), parse_filter(args.eval))
        for case in cases:
            base_prompt = case.prompt if args.same_prompt else baseline_prompt(case)
            skill_prompt = case.prompt
            baseline_output = args.output_dir / "baseline" / case.skill / f"{case.eval_id}.md"
            skill_output = args.output_dir / "skill-explicit" / case.skill / f"{case.eval_id}.md"
            if args.dry_run:
                print(f"{case.skill}/{case.eval_id}")
                print(f"  baseline prompt: {base_prompt}")
                print(f"  skill prompt: {skill_prompt}")
                continue
            run_command(args.baseline_command, case, "baseline", base_prompt, baseline_output, args.timeout_seconds)
            run_command(args.skill_command, case, "skill-explicit", skill_prompt, skill_output, args.timeout_seconds)
            print(f"Wrote real-model answers for {case.skill}/{case.eval_id}.")
    except Exception as exc:
        print(f"Answer arm run failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
