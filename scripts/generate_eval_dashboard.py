#!/usr/bin/env python3
"""Generate a static dashboard from UXL evaluator scorecards."""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"{path}: missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def git_value(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def run_url() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return ""


def commit_metadata(label: str) -> dict[str, str]:
    sha = os.environ.get("GITHUB_SHA") or git_value(["rev-parse", "HEAD"])
    ref_name = os.environ.get("GITHUB_REF_NAME") or git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    message = git_value(["show", "-s", "--format=%s", sha]) if sha else ""
    committed_at = git_value(["show", "-s", "--format=%cI", sha]) if sha else ""
    return {
        "label": label,
        "commit_sha": sha,
        "short_sha": sha[:7] if sha else "",
        "ref_name": ref_name,
        "commit_message": message,
        "committed_at": committed_at,
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
        "run_url": run_url(),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
    }


def round_score(value: Any) -> float:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return 0.0


def answer_track(answer: dict[str, Any] | None) -> dict[str, Any]:
    if not answer:
        return {
            "available": False,
            "case_count": 0,
            "skill_count": 0,
            "baseline_average": 0.0,
            "skill_average": 0.0,
            "delta": 0.0,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "missing_skill": 0,
            "forbidden_hits": 0,
            "skills": [],
            "cases": [],
        }
    summary = answer.get("summary", {})
    return {
        "available": True,
        "case_count": int(summary.get("case_count", 0)),
        "skill_count": int(summary.get("skill_count", 0)),
        "baseline_average": round_score(summary.get("baseline_average")),
        "skill_average": round_score(summary.get("skill_average")),
        "delta": round_score(summary.get("delta")),
        "wins": int(summary.get("skill_wins", 0)),
        "losses": int(summary.get("skill_losses", 0)),
        "ties": int(summary.get("ties", 0)),
        "missing_skill": int(summary.get("missing_skill", 0)),
        "forbidden_hits": int(summary.get("skill_forbidden_hits", 0)),
        "skills": answer.get("skills", []),
        "cases": answer.get("cases", []),
    }


def executable_track(executable: dict[str, Any] | None) -> dict[str, Any]:
    if not executable:
        return {
            "available": False,
            "task_count": 0,
            "skill_count": 0,
            "passed": 0,
            "missing_candidates": 0,
            "pass_rate": 0.0,
            "skills": [],
            "tasks": [],
        }
    summary = executable.get("summary", {})
    return {
        "available": True,
        "task_count": int(summary.get("task_count", 0)),
        "skill_count": int(summary.get("skill_count", 0)),
        "passed": int(summary.get("passed", 0)),
        "missing_candidates": int(summary.get("missing_candidates", 0)),
        "pass_rate": round_score(summary.get("average")),
        "skills": executable.get("skills", []),
        "tasks": executable.get("cases", []),
    }


def skill_rows(answer: dict[str, Any], executable: dict[str, Any]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for item in answer.get("skills", []):
        skill = str(item.get("skill", "unknown"))
        rows.setdefault(skill, {"skill": skill})
        rows[skill].update(
            {
                "answer_cases": int(item.get("cases", 0)),
                "answer_skill_average": round_score(item.get("skill_average")),
                "answer_delta": round_score(item.get("delta")),
                "answer_forbidden_hits": int(item.get("skill_forbidden_hits", 0)),
            }
        )
    for item in executable.get("skills", []):
        skill = str(item.get("skill", "unknown"))
        rows.setdefault(skill, {"skill": skill})
        rows[skill].update(
            {
                "executable_tasks": int(item.get("tasks", 0)),
                "executable_passed": int(item.get("passed", 0)),
                "executable_pass_rate": round_score(item.get("average")),
            }
        )
    return [rows[key] for key in sorted(rows)]


def load_history(paths: list[Path]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in paths:
        data = load_json(path)
        if not data:
            continue
        if isinstance(data.get("runs"), list):
            runs.extend(item for item in data["runs"] if isinstance(item, dict))
        elif isinstance(data.get("current"), dict):
            runs.append(data["current"])
        elif "commit" in data and "tracks" in data:
            runs.append(data)
    return runs


def dedupe_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for run in runs:
        commit = run.get("commit", {})
        key = (
            str(commit.get("commit_sha", "")),
            str(commit.get("run_id", "")),
            str(commit.get("label", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(run)
    return result


def regression_notes(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if previous is None:
        return []
    notes: list[str] = []
    previous_answer = previous.get("tracks", {}).get("answer_quality", {})
    current_answer = current.get("tracks", {}).get("answer_quality", {})
    previous_exec = previous.get("tracks", {}).get("executable_tasks", {})
    current_exec = current.get("tracks", {}).get("executable_tasks", {})

    if current_answer.get("available") and previous_answer.get("available"):
        delta = round_score(current_answer.get("skill_average")) - round_score(previous_answer.get("skill_average"))
        if delta < 0:
            notes.append(f"Answer skill average dropped {delta:+.4f} from previous run.")
        delta_score = round_score(current_answer.get("delta")) - round_score(previous_answer.get("delta"))
        if delta_score < 0:
            notes.append(f"Answer delta dropped {delta_score:+.4f} from previous run.")
    if current_exec.get("available") and previous_exec.get("available"):
        pass_delta = round_score(current_exec.get("pass_rate")) - round_score(previous_exec.get("pass_rate"))
        if pass_delta < 0:
            notes.append(f"Executable pass rate dropped {pass_delta:+.4f} from previous run.")
    return notes


def build_current(
    answer: dict[str, Any] | None,
    executable: dict[str, Any] | None,
    label: str,
    answer_path: Path | None,
    executable_path: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    answer_summary = answer_track(answer)
    executable_summary = executable_track(executable)
    links = {}
    if answer_path:
        links["answer_scorecard"] = Path(os.path.relpath(answer_path, output_dir)).as_posix()
        markdown = answer_path.with_suffix(".md")
        if markdown.exists():
            links["answer_markdown"] = Path(os.path.relpath(markdown, output_dir)).as_posix()
    if executable_path:
        links["executable_scorecard"] = Path(os.path.relpath(executable_path, output_dir)).as_posix()
        markdown = executable_path.with_suffix(".md")
        if markdown.exists():
            links["executable_markdown"] = Path(os.path.relpath(markdown, output_dir)).as_posix()

    return {
        "schema_version": "0",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": commit_metadata(label),
        "tracks": {
            "answer_quality": answer_summary,
            "executable_tasks": executable_summary,
        },
        "skills": skill_rows(answer_summary, executable_summary),
        "links": links,
    }


def status_for(run: dict[str, Any]) -> str:
    answer = run.get("tracks", {}).get("answer_quality", {})
    executable = run.get("tracks", {}).get("executable_tasks", {})
    if answer.get("forbidden_hits", 0) or answer.get("missing_skill", 0) or executable.get("missing_candidates", 0):
        return "attention"
    if answer.get("available") and round_score(answer.get("delta")) < 0:
        return "regression"
    if executable.get("available") and round_score(executable.get("pass_rate")) < 1.0:
        return "attention"
    return "pass"


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: Any, signed: bool = False) -> str:
    score = round_score(value)
    return f"{score:+.4f}" if signed else f"{score:.4f}"


def fmt_optional(value: Any, signed: bool = False) -> str:
    if value is None:
        return "n/a"
    return fmt(value, signed=signed)


def count_optional(row: dict[str, Any], key: str) -> str:
    return str(row[key]) if key in row else "n/a"


def passed_optional(row: dict[str, Any]) -> str:
    if "executable_passed" not in row or "executable_tasks" not in row:
        return "n/a"
    return f"{row['executable_passed']}/{row['executable_tasks']}"


def metric(title: str, value: str, subtext: str, tone: str = "") -> str:
    return (
        f'<section class="metric {esc(tone)}"><div class="metric-title">{esc(title)}</div>'
        f'<div class="metric-value">{esc(value)}</div><div class="metric-subtext">{esc(subtext)}</div></section>'
    )


def trend_svg(runs: list[dict[str, Any]], path: list[str], label: str, color: str) -> str:
    values = []
    for run in runs:
        value: Any = run
        for key in path:
            value = value.get(key, {}) if isinstance(value, dict) else {}
        values.append(round_score(value))
    width = 680
    height = 180
    pad = 28
    if len(values) == 1:
        x_values = [width // 2]
    else:
        x_values = [pad + index * (width - 2 * pad) / (len(values) - 1) for index in range(len(values))]
    y_values = [height - pad - value * (height - 2 * pad) for value in values]
    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(x_values, y_values, strict=True))
    circles = "\n".join(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4"><title>{esc(label)}: {value:.4f}</title></circle>'
        for x, y, value in zip(x_values, y_values, values, strict=True)
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)} trend">'
        f'<line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" />'
        f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" />'
        f'<polyline points="{points}" style="stroke:{esc(color)}" />{circles}</svg>'
    )


def test_rows(current: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    answer = current["tracks"]["answer_quality"]
    executable = current["tracks"]["executable_tasks"]
    for case in answer.get("cases", []):
        skill = case.get("skill", "")
        eval_id = case.get("eval_id", "")
        baseline = case.get("baseline", {})
        skill_explicit = case.get("skill_explicit", {})
        notes = "; ".join(skill_explicit.get("notes", [])) if skill_explicit.get("notes") else "pass"
        rows.append(
            {
                "track": "answer quality",
                "skill": skill,
                "test": eval_id,
                "score": round_score(skill_explicit.get("score")),
                "detail": (
                    f"baseline {fmt(baseline.get('score'))}, skill {fmt(skill_explicit.get('score'))}, "
                    f"delta {fmt(case.get('delta'), signed=True)}; {notes}"
                ),
            }
        )
    for case in executable.get("tasks", []):
        notes = "; ".join(case.get("notes", [])) if case.get("notes") else "pass"
        rows.append(
            {
                "track": "executable task",
                "skill": case.get("skill", ""),
                "test": case.get("task", ""),
                "score": round_score(case.get("score")),
                "detail": notes,
            }
        )
    return rows


def render_html(data: dict[str, Any]) -> str:
    current = data["current"]
    commit = current["commit"]
    answer = current["tracks"]["answer_quality"]
    executable = current["tracks"]["executable_tasks"]
    regressions = data["regressions"]
    status = status_for(current)
    run_link = commit.get("run_url") or ""
    run_text = f'<a href="{esc(run_link)}">{esc(commit.get("run_id", "workflow run"))}</a>' if run_link else "local run"

    regression_html = (
        "<ul>" + "".join(f"<li>{esc(note)}</li>" for note in regressions) + "</ul>"
        if regressions
        else "<p>No regressions detected against the supplied history.</p>"
    )

    history_rows = "\n".join(
        "<tr>"
        f"<td>{esc(run.get('commit', {}).get('short_sha', ''))}</td>"
        f"<td>{esc(run.get('commit', {}).get('ref_name', ''))}</td>"
        f"<td>{esc(run.get('commit', {}).get('label', ''))}</td>"
        f"<td>{fmt(run.get('tracks', {}).get('answer_quality', {}).get('skill_average'))}</td>"
        f"<td>{fmt(run.get('tracks', {}).get('answer_quality', {}).get('delta'), signed=True)}</td>"
        f"<td>{fmt(run.get('tracks', {}).get('executable_tasks', {}).get('pass_rate'))}</td>"
        f"<td><span class=\"status {esc(status_for(run))}\">{esc(status_for(run))}</span></td>"
        "</tr>"
        for run in data["runs"]
    )
    latest_rows_html = "\n".join(
        "<tr>"
        f"<td>{esc(row['track'])}</td>"
        f"<td><code>{esc(row['skill'])}</code></td>"
        f"<td><code>{esc(row['test'])}</code></td>"
        f"<td>{fmt(row['score'])}</td>"
        f"<td>{esc(row['detail'])}</td>"
        "</tr>"
        for row in test_rows(current)
    )
    skill_rows_html = "\n".join(
        "<tr>"
        f"<td><code>{esc(row.get('skill', ''))}</code></td>"
        f"<td>{fmt_optional(row.get('answer_skill_average'))}</td>"
        f"<td>{fmt_optional(row.get('answer_delta'), signed=True)}</td>"
        f"<td>{esc(count_optional(row, 'answer_cases'))}</td>"
        f"<td>{fmt_optional(row.get('executable_pass_rate'))}</td>"
        f"<td>{esc(passed_optional(row))}</td>"
        f"<td>{esc(count_optional(row, 'answer_forbidden_hits'))}</td>"
        "</tr>"
        for row in current["skills"]
    )
    artifact_links = "".join(
        f'<li><a href="{esc(target)}">{esc(name.replace("_", " "))}</a></li>'
        for name, target in current.get("links", {}).items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UXL Skill Evaluation Dashboard</title>
  <style>
    :root {{
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #1f2933;
      --muted: #5f6b7a;
      --line: #d8dee7;
      --blue: #2364aa;
      --green: #147a3e;
      --amber: #986b00;
      --red: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    .wrap {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0;
    }}
    .eyebrow {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    h1 {{
      margin: 4px 0 8px;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.1;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    a {{ color: var(--blue); }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 18px;
      color: var(--muted);
      font-size: 14px;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-height: 116px;
    }}
    .metric-title {{
      color: var(--muted);
      font-size: 13px;
    }}
    .metric-value {{
      font-size: 30px;
      font-weight: 700;
      margin-top: 8px;
      letter-spacing: 0;
    }}
    .metric-subtext {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }}
    .metric.pass .metric-value {{ color: var(--green); }}
    .metric.attention .metric-value {{ color: var(--amber); }}
    .metric.regression .metric-value {{ color: var(--red); }}
    main .wrap {{
      display: grid;
      gap: 20px;
    }}
    section.block {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      overflow: hidden;
    }}
    .charts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .chart {{
      min-height: 240px;
    }}
    svg {{
      width: 100%;
      height: 180px;
      margin-top: 8px;
    }}
    svg line {{
      stroke: var(--line);
      stroke-width: 1.5;
    }}
    svg polyline {{
      fill: none;
      stroke-width: 3;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    svg circle {{
      fill: #ffffff;
      stroke: currentColor;
      stroke-width: 2;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      background: #fbfcfd;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 0.95em;
    }}
    .status {{
      display: inline-block;
      min-width: 86px;
      border-radius: 999px;
      padding: 2px 8px;
      text-align: center;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .status.pass {{ color: var(--green); background: #e7f5ec; }}
    .status.attention {{ color: var(--amber); background: #fff4d6; }}
    .status.regression {{ color: var(--red); background: #fde8e7; }}
    ul {{ margin: 8px 0 0; padding-left: 20px; }}
    @media (max-width: 720px) {{
      .wrap {{ width: min(100vw - 20px, 1180px); padding: 18px 0; }}
      table {{ display: block; overflow-x: auto; white-space: nowrap; }}
      .metric-value {{ font-size: 26px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">UXL Skill Evaluation</div>
      <h1>Commit Performance Dashboard</h1>
      <div class="meta">
        <span>Commit <code>{esc(commit.get("short_sha", ""))}</code></span>
        <span>{esc(commit.get("commit_message", ""))}</span>
        <span>Ref <code>{esc(commit.get("ref_name", ""))}</code></span>
        <span>{run_text}</span>
        <span><span class="status {esc(status)}">{esc(status)}</span></span>
      </div>
      <div class="metric-grid">
        {metric("Answer Skill Average", fmt(answer.get("skill_average")), f"{answer.get("case_count", 0)} cases", status)}
        {metric("Answer Delta", fmt(answer.get("delta"), signed=True), f"{answer.get("wins", 0)} wins, {answer.get("losses", 0)} losses", "pass" if round_score(answer.get("delta")) >= 0 else "regression")}
        {metric("Executable Pass Rate", fmt(executable.get("pass_rate")), f"{executable.get("passed", 0)} of {executable.get("task_count", 0)} tasks", "pass" if round_score(executable.get("pass_rate")) >= 1.0 else "attention")}
        {metric("Forbidden Hits", str(answer.get("forbidden_hits", 0)), "unsupported claim checks", "pass" if not answer.get("forbidden_hits", 0) else "attention")}
        {metric("Missing Outputs", str(answer.get("missing_skill", 0) + executable.get("missing_candidates", 0)), "answers plus executable candidates", "pass" if not (answer.get("missing_skill", 0) + executable.get("missing_candidates", 0)) else "attention")}
      </div>
    </div>
  </header>
  <main>
    <div class="wrap">
      <section class="block">
        <h2>Regression Notes</h2>
        {regression_html}
      </section>
      <section class="block charts">
        <div class="chart">
          <h2>Answer Skill Average</h2>
          {trend_svg(data["runs"], ["tracks", "answer_quality", "skill_average"], "Answer skill average", "#2364aa")}
        </div>
        <div class="chart">
          <h2>Executable Pass Rate</h2>
          {trend_svg(data["runs"], ["tracks", "executable_tasks", "pass_rate"], "Executable pass rate", "#147a3e")}
        </div>
      </section>
      <section class="block">
        <h2>Latest Tests</h2>
        <table>
          <thead><tr><th>Track</th><th>Skill</th><th>Test</th><th>Score</th><th>Detail</th></tr></thead>
          <tbody>{latest_rows_html}</tbody>
        </table>
      </section>
      <section class="block">
        <h2>Per Skill</h2>
        <table>
          <thead><tr><th>Skill</th><th>Answer avg</th><th>Delta</th><th>Cases</th><th>Executable pass rate</th><th>Passed</th><th>Forbidden hits</th></tr></thead>
          <tbody>{skill_rows_html}</tbody>
        </table>
      </section>
      <section class="block">
        <h2>Commit History</h2>
        <table>
          <thead><tr><th>Commit</th><th>Ref</th><th>Label</th><th>Answer avg</th><th>Delta</th><th>Executable pass rate</th><th>Status</th></tr></thead>
          <tbody>{history_rows}</tbody>
        </table>
      </section>
      <section class="block">
        <h2>Artifacts</h2>
        <ul>
          <li><a href="dashboard-data.json">dashboard data</a></li>
          <li><a href="run-record.json">current run record</a></li>
          {artifact_links}
        </ul>
      </section>
    </div>
  </main>
</body>
</html>
"""


def render_summary(data: dict[str, Any]) -> str:
    current = data["current"]
    commit = current["commit"]
    answer = current["tracks"]["answer_quality"]
    executable = current["tracks"]["executable_tasks"]
    run_url_value = commit.get("run_url") or ""
    run_label = f"[{commit.get('run_id', 'run')}]({run_url_value})" if run_url_value else "local run"
    lines = [
        "# UXL Skill Evaluation Dashboard",
        "",
        f"Commit `{commit.get('short_sha', '')}` on `{commit.get('ref_name', '')}`: {commit.get('commit_message', '')}",
        f"Workflow run: {run_label}",
        "",
        "| Track | Score | Detail |",
        "| --- | ---: | --- |",
        (
            f"| Answer quality | {fmt(answer.get('skill_average'))} | "
            f"delta {fmt(answer.get('delta'), signed=True)}, {answer.get('skill_count', 0)} skills, "
            f"{answer.get('case_count', 0)} cases, "
            f"{answer.get('forbidden_hits', 0)} forbidden hits |"
        ),
        (
            f"| Executable tasks | {fmt(executable.get('pass_rate'))} | "
            f"{executable.get('skill_count', 0)} skills, {executable.get('passed', 0)} of "
            f"{executable.get('task_count', 0)} tasks passed, "
            f"{executable.get('missing_candidates', 0)} missing candidates |"
        ),
    ]
    rows = test_rows(current)
    if rows:
        lines.extend(
            [
                "",
                "## Tests",
                "",
                "| Track | Skill | Test | Score | Detail |",
                "| --- | --- | --- | ---: | --- |",
            ]
        )
        for row in rows:
            detail = str(row["detail"]).replace("|", "\\|")
            lines.append(
                f"| {row['track']} | `{row['skill']}` | `{row['test']}` | {fmt(row['score'])} | {detail} |"
            )
    if data["regressions"]:
        lines.extend(["", "## Regressions", ""])
        lines.extend(f"- {note}" for note in data["regressions"])
    else:
        lines.extend(["", "No regressions detected against the supplied history."])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer-scorecard", type=Path, help="Path to scorecard.json from compare_eval_arms.py.")
    parser.add_argument(
        "--executable-scorecard",
        type=Path,
        help="Path to executable-scorecard.json from run_executable_tasks.py.",
    )
    parser.add_argument("--history-file", action="append", type=Path, default=[], help="Prior dashboard-data.json files.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for dashboard outputs.")
    parser.add_argument("--label", default="manual", help="Human-readable run label.")
    parser.add_argument("--write-github-summary", action="store_true", help="Append summary to $GITHUB_STEP_SUMMARY.")
    args = parser.parse_args(argv)

    if not args.answer_scorecard and not args.executable_scorecard:
        print("Provide at least one scorecard input.", file=sys.stderr)
        return 1

    answer = load_json(args.answer_scorecard)
    executable = load_json(args.executable_scorecard)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    current = build_current(answer, executable, args.label, args.answer_scorecard, args.executable_scorecard, args.output_dir)
    history = load_history(args.history_file)
    previous = history[-1] if history else None
    regressions = regression_notes(previous, current)
    runs = dedupe_runs([*history, current])
    data = {
        "schema_version": "0",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "current": current,
        "runs": runs,
        "regressions": regressions,
    }

    (args.output_dir / "run-record.json").write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "dashboard-data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "summary.md").write_text(render_summary(data), encoding="utf-8")
    (args.output_dir / "index.html").write_text(render_html(data), encoding="utf-8")

    summary = render_summary(data)
    print(summary)
    if args.write_github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write(summary)
                handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
