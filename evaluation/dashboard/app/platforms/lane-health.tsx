"use client";

import { useEffect, useMemo, useState } from "react";
import { StatusPill } from "../components";
import type { TargetQualification } from "../data";

function expiresAt(record: TargetQualification) {
  return new Date(new Date(record.recordedAt).getTime() + record.maxAgeDays * 86_400_000);
}

export function LaneHealth({ qualifications }: { qualifications: TargetQualification[] }) {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    const timer = window.setTimeout(() => setNow(Date.now()), 0);
    return () => window.clearTimeout(timer);
  }, []);
  const latest = useMemo(() => {
    const records = new Map<string, TargetQualification>();
    for (const record of qualifications) {
      const previous = records.get(record.laneId);
      if (!previous || previous.recordedAt < record.recordedAt) records.set(record.laneId, record);
    }
    return [...records.values()].sort((left, right) => left.displayName.localeCompare(right.displayName));
  }, [qualifications]);

  if (latest.length === 0) {
    return <article className="adapter-card"><div><StatusPill tone="planned">No retained qualifications</StatusPill><span>Evidence required</span></div><h3>No specialized lane is current.</h3><p>Commit a reviewed sanitized qualification record after its fixed oracle passes.</p></article>;
  }

  return latest.map((record) => {
    const expired = now !== null && expiresAt(record).getTime() < now;
    const changed = record.repositoryStatus === "changed";
    const current = now !== null && !expired && !changed;
    const label = changed ? "Repository changed" : expired ? "Age expired" : now === null ? "Checking" : "Current";
    return (
      <article className={`adapter-card lane-record ${current ? "proven" : "stale"}`} key={record.id}>
        <div><StatusPill tone={current ? "good" : changed || expired ? "watch" : "neutral"}>{label}</StatusPill><span>Qualification only</span></div>
        <h3>{record.displayName}</h3>
        <dl>
          <div><dt>Vendor</dt><dd>{record.vendor}</dd></div>
          <div><dt>Device</dt><dd>{record.device}</dd></div>
          <div><dt>Interface</dt><dd>{record.interface}</dd></div>
          <div><dt>Oracle task</dt><dd>{record.task}</dd></div>
          <div><dt>Qualified</dt><dd>{record.recordedAt.slice(0, 10)}</dd></div>
          <div><dt>Expires</dt><dd>{expiresAt(record).toISOString().slice(0, 10)}</dd></div>
        </dl>
        <p className="lane-limitation">{record.limitations[0]}</p>
        <a href={`https://github.com/uxlfoundation/skills/blob/main/${record.source}`}>Inspect sanitized record ↗</a>
      </article>
    );
  });
}
