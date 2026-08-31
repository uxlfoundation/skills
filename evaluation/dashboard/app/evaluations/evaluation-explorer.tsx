"use client";

import { useEffect, useMemo, useState } from "react";
import type { EvaluationTask } from "../data";

type TaskRecord = EvaluationTask & { skill: string; project: string };

function titleCase(value: string) {
  return value.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
}

export function EvaluationExplorer({ tasks, projects }: { tasks: TaskRecord[]; projects: string[] }) {
  const [query, setQuery] = useState("");
  const [project, setProject] = useState("all");
  const [status, setStatus] = useState("all");
  const [evidence, setEvidence] = useState("all");

  useEffect(() => {
    const openLinkedRecord = () => {
      if (!window.location.hash) return;
      const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
      if (target instanceof HTMLDetailsElement) target.open = true;
    };
    openLinkedRecord();
    window.addEventListener("hashchange", openLinkedRecord);
    return () => window.removeEventListener("hashchange", openLinkedRecord);
  }, []);

  const visible = useMemo(() => {
    const needle = query.toLowerCase().trim();
    return tasks.filter((task) => {
      const haystack = [task.name, task.project, task.role, task.environment, ...task.covers].join(" ").toLowerCase();
      return (!needle || haystack.includes(needle))
        && (project === "all" || task.project === project)
        && (status === "all" || task.status === status)
        && (evidence === "all" || task.calibration === evidence);
    });
  }, [evidence, project, query, status, tasks]);

  return (
    <div className="explorer">
      <div className="explorer-controls">
        <label className="search-field"><span>Search evaluations</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Task, project, or capability" /></label>
        <label><span>Project</span><select value={project} onChange={(event) => setProject(event.target.value)}><option value="all">All projects</option>{projects.map((name) => <option key={name}>{name}</option>)}</select></label>
        <label><span>Status</span><select value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All statuses</option><option value="implemented">Implemented</option><option value="planned">Planned</option></select></label>
        <label><span>Evidence</span><select value={evidence} onChange={(event) => setEvidence(event.target.value)}><option value="all">All evidence</option><option value="headroom">Headroom</option><option value="ceiling">Ceiling</option><option value="manual">Manual</option><option value="uncalibrated">Uncalibrated</option></select></label>
      </div>
      <div className="result-count" aria-live="polite"><strong>{visible.length}</strong> of {tasks.length} evaluations</div>
      <div className="evaluation-list">
        {visible.map((task) => (
          <details className="evaluation-record" id={task.name} key={task.name}>
            <summary>
              <span className={`record-state ${task.status}`}>{task.status}</span>
              <span><b>{task.name}</b><small>{task.project}</small></span>
              <span><b>{titleCase(task.calibration)}</b><small>{titleCase(task.role)}</small></span>
              <span><b>{titleCase(task.environment)}</b><small>{titleCase(task.track)}</small></span>
              <i aria-hidden="true">+</i>
            </summary>
            <div className="evaluation-body">
              <div>
                <p className="section-label">Capabilities exercised</p>
                <div className="tag-row">{task.covers.map((item) => <span key={item}>{titleCase(item)}</span>)}</div>
              </div>
              <dl>
                <div><dt>Reproduction</dt><dd>{titleCase(task.reproduction)}</dd></div>
                <div><dt>Origin</dt><dd>{titleCase(task.origin)}</dd></div>
                <div><dt>Hardware contract</dt><dd>{titleCase(task.hardware)}</dd></div>
                <div><dt>Workflow</dt><dd>{task.workflow.map(titleCase).join(" → ")}</dd></div>
                <div><dt>Matched evidence</dt><dd>{task.evaluationCells.length > 0 ? `${task.evaluationCells.length} retained cell${task.evaluationCells.length === 1 ? "" : "s"}` : "Not yet recorded in the v1 contract"}</dd></div>
              </dl>
              {task.evaluationCells.slice(-1).map((cell) => (
                <dl key={cell.id} aria-label="Latest matched evaluation evidence">
                  <div><dt>Latest cell</dt><dd>{cell.stage} · {cell.attemptsPerArm} attempts per arm</dd></div>
                  <div><dt>Agent / model</dt><dd>{cell.agent} · {cell.model}</dd></div>
                  <div><dt>Environment</dt><dd>{titleCase(cell.environment)} · {titleCase(cell.hardware)}</dd></div>
                  <div><dt>Recorded</dt><dd>{cell.recordedAt.slice(0, 10)} · max age {cell.maxAgeDays} days</dd></div>
                </dl>
              ))}
              <a href={`https://github.com/uxlfoundation/skills/tree/main/evaluation/harbor/tasks/${task.name}`}>Inspect task and verifier ↗</a>
              {task.evaluationCells.slice(-1).map((cell) => <a key={cell.id} href={`https://github.com/uxlfoundation/skills/blob/main/${cell.source}`}>Inspect matched evidence ↗</a>)}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
