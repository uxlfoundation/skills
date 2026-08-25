import { PageIntro, SiteFooter, SiteHeader, StatusPill } from "../components";
import { allTasks, skills, titleCase } from "../data";

export const dynamic = "force-static";

const environmentOrder = ["hosted-cpu", "hosted-container", "hosted-toolchain", "manual-gpu", "target-device", "target-gpu", "target-distributed"];
const environmentCopy: Record<string, { title: string; description: string; group: string }> = {
  "hosted-cpu": { title: "Hosted CPU", description: "Portable correctness, integration, and executable smoke coverage.", group: "Available now" },
  "hosted-container": { title: "Hosted container", description: "Pinned fixtures for discriminating reasoning and answer-quality checks.", group: "Available now" },
  "hosted-toolchain": { title: "Hosted toolchain", description: "Compiler, loader, and cross-project SYCL environment checks.", group: "Available now" },
  "manual-gpu": { title: "Specialized GPU", description: "Manually approved device-dependent evaluation through a controlled runner.", group: "Adapter qualified" },
  "target-device": { title: "Target device", description: "Portable accelerator tasks awaiting representative machine evidence.", group: "Planned coverage" },
  "target-gpu": { title: "Target GPU", description: "Project-specific GPU paths that cannot be represented faithfully on hosted compute.", group: "Planned coverage" },
  "target-distributed": { title: "Distributed system", description: "Topology, rank, worker, and communication evidence across controlled systems.", group: "Planned coverage" },
};

const matrixGroups = [
  { label: "Hosted CPU", environments: ["hosted-cpu"] },
  { label: "Container", environments: ["hosted-container"] },
  { label: "Toolchain", environments: ["hosted-toolchain"] },
  { label: "GPU", environments: ["manual-gpu", "target-gpu"] },
  { label: "Target device", environments: ["target-device"] },
  { label: "Distributed", environments: ["target-distributed"] },
];

export default function PlatformsPage() {
  const environments = environmentOrder.map((name) => {
    const tasks = allTasks.filter((task) => task.environment === name);
    return {
      name,
      ...environmentCopy[name],
      total: tasks.length,
      implemented: tasks.filter((task) => task.status === "implemented").length,
      projects: new Set(tasks.map((task) => task.project)).size,
    };
  });

  return (
    <main>
      <SiteHeader prefix="../" active="platforms" />
      <PageIntro label="Platform evidence" title={<>Evidence contract first.<br />Hardware second.</>}>
        Hosted systems remain the default. Specialized machines join only when a task requires a particular device, backend, topology, driver, or instruction set.
      </PageIntro>

      <section className="platform-principles section-pad">
        <div><span>01</span><h3>Vendor neutral</h3><p>No platform receives preferred status. The same task, verifier, revision, and provenance rules apply everywhere.</p></div>
        <div><span>02</span><h3>Capability matched</h3><p>A task moves to specialized hardware only when hosted infrastructure cannot reproduce the behavior faithfully.</p></div>
        <div><span>03</span><h3>Evidence portable</h3><p>Approved systems return the same Harbor result structure, so evaluation remains comparable and reviewable.</p></div>
      </section>

      <section className="environment-section section-pad">
        <div className="section-heading compact">
          <div><p className="section-label">Execution coverage</p><h2>Where the portfolio runs today.</h2></div>
          <p>Counts describe evaluation environments, not hardware market coverage or vendor performance.</p>
        </div>
        <div className="environment-grid">
          {environments.map((environment) => (
            <article className="environment-card" key={environment.name}>
              <div><StatusPill tone={environment.implemented > 0 ? "good" : "planned"}>{environment.group}</StatusPill><span>{titleCase(environment.name)}</span></div>
              <h3>{environment.title}</h3><p>{environment.description}</p>
              <dl><div><dt>Implemented</dt><dd>{environment.implemented}</dd></div><div><dt>Total tasks</dt><dd>{environment.total}</dd></div><div><dt>Projects</dt><dd>{environment.projects}</dd></div></dl>
            </article>
          ))}
        </div>

        <div className="platform-matrix-wrap">
          <div className="section-heading compact inverse">
            <div><p className="section-label">Project matrix</p><h2>Environment evidence by skill.</h2></div>
            <p>A dash means that the current evaluation portfolio does not claim that environment for the project.</p>
          </div>
          <div className="platform-matrix" role="table" aria-label="Evaluation environment coverage by skill">
            <div className="platform-matrix-row platform-matrix-head" role="row"><span>Project skill</span>{matrixGroups.map((group) => <span key={group.label}>{group.label}</span>)}</div>
            {skills.map((skill) => (
              <a href={`../skills/#${skill.name}`} className="platform-matrix-row" role="row" key={skill.name}>
                <span>{skill.displayName}</span>
                {matrixGroups.map((group) => {
                  const tasks = skill.tasks.filter((task) => group.environments.includes(task.environment));
                  const implemented = tasks.filter((task) => task.status === "implemented").length;
                  return <span className={tasks.length === 0 ? "no-claim" : implemented === tasks.length ? "verified" : "planned-cell"} key={group.label}>{tasks.length === 0 ? "—" : <><b>{implemented}</b><small>/{tasks.length}</small></>}</span>;
                })}
              </a>
            ))}
          </div>
        </div>
      </section>

      <section className="adapter-section section-pad">
        <div className="section-heading">
          <div><p className="section-label">Specialized adapters</p><h2>One proof of concept.<br />An open pattern for every member.</h2></div>
          <p>An adapter qualifies dispatch and evidence collection. It does not prove that a skill helps, and it does not give its hardware vendor priority in the portfolio.</p>
        </div>
        <div className="adapter-grid">
          <article className="adapter-card proven">
            <div><StatusPill tone="good">Runner qualified</StatusPill><span>Proof of concept</span></div>
            <h3>Windows / WSL GPU adapter</h3>
            <dl><div><dt>Vendor</dt><dd>Intel</dd></div><div><dt>Device</dt><dd>Arc B580</dd></div><div><dt>Qualification</dt><dd>Oracle passed</dd></div><div><dt>Skill comparison</dt><dd>Not yet run</dd></div></dl>
            <a href="https://github.com/uxlfoundation/skills/blob/main/docs/self-hosted-runners.md">Review shared runner contract ↗</a>
          </article>
          <article className="adapter-card open">
            <div><StatusPill tone="planned">Open adapter slots</StatusPill><span>Member contribution</span></div>
            <h3>Bring another environment</h3>
            <p>Any UXL member can add a controlled CPU, GPU, accelerator, or distributed environment by implementing the same qualification, provenance, and artifact contract.</p>
            <ul><li>Declare the required capability</li><li>Run only reviewed evaluator revisions</li><li>Qualify with a reward-1.0 oracle</li><li>Return complete, sanitized evidence</li></ul>
          </article>
        </div>
        <p className="platform-footnote">The portfolio currently spans {skills.length} skills. Vendor or device names appear only where accepted environment evidence exists.</p>
      </section>
      <SiteFooter prefix="../" />
    </main>
  );
}
