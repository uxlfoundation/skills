"use client";

import { useEffect, useMemo, useState } from "react";
import type { EvaluationCell } from "../data";

function expiresAt(cell: EvaluationCell) {
  return new Date(new Date(cell.recordedAt).getTime() + cell.maxAgeDays * 86_400_000);
}

function configurationKey(cell: EvaluationCell) {
  return [cell.agent, cell.harness, cell.harnessVersion, cell.model, cell.reasoningEffort, cell.environment, cell.hardware].join("|");
}

export function EvidenceHealth({ cells }: { cells: EvaluationCell[] }) {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    const timer = window.setTimeout(() => setNow(Date.now()), 0);
    return () => window.clearTimeout(timer);
  }, []);
  const health = useMemo(() => {
    const expired = now === null ? 0 : cells.filter((cell) => expiresAt(cell).getTime() < now).length;
    const changed = cells.filter((cell) => cell.repositoryStatus === "changed").length;
    const current = now === null ? 0 : cells.length - new Set([
      ...cells.filter((cell) => expiresAt(cell).getTime() < now).map((cell) => cell.id),
      ...cells.filter((cell) => cell.repositoryStatus === "changed").map((cell) => cell.id),
    ]).size;
    return {
      current,
      expired,
      changed,
      configurations: new Set(cells.map(configurationKey)).size,
    };
  }, [cells, now]);

  return (
    <section className="evidence-health section-pad" aria-label="Matched evidence health">
      <div className="section-heading compact">
        <div><p className="section-label">Matched evidence health</p><h2>Exact claims, visible freshness.</h2></div>
        <p>Cells are never merged into a universal score. Each row keeps its model, harness, software, environment, and hardware context.</p>
      </div>
      <div className="evidence-health-summary">
        <div><strong>{now === null ? "—" : health.current}</strong><span>current cells</span></div>
        <div><strong>{health.expired}</strong><span>age-expired</span></div>
        <div><strong>{health.changed}</strong><span>repository changed</span></div>
        <div><strong>{health.configurations}</strong><span>tested configurations</span></div>
      </div>
      {cells.length === 0 ? (
        <div className="evidence-empty"><h3>No v1 cells retained yet.</h3><p>The task portfolio and historical calibration labels remain visible, but current-proof status begins only when a reviewed matched cell is committed.</p></div>
      ) : (
        <div className="evidence-table-wrap">
          <table className="evidence-table">
            <thead><tr><th>Task</th><th>Stage</th><th>Agent / model</th><th>Harness</th><th>Environment</th><th>Recorded</th><th>Health</th></tr></thead>
            <tbody>{cells.slice().reverse().map((cell) => {
              const expired = now !== null && expiresAt(cell).getTime() < now;
              const status = cell.repositoryStatus === "changed" ? `Changed: ${cell.repositoryChanges.join(", ")}` : expired ? "Age-expired" : now === null ? "Checking" : "Current";
              return <tr key={cell.id}><td>{cell.task}</td><td>{cell.stage}</td><td>{cell.agent} / {cell.model}</td><td>{cell.harness} {cell.harnessVersion}</td><td>{cell.environment} / {cell.hardware}</td><td>{cell.recordedAt.slice(0, 10)}</td><td>{status}</td></tr>;
            })}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
