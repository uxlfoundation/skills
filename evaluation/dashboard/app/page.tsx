import { Eyebrow, SiteFooter, SiteHeader, StatusPill } from "./components";
import { capabilityClasses, capabilityCoverage, portfolio, skillStats, skills, sourceFreshness } from "./data";

const summary = [
  { value: String(portfolio.skills), label: "published skills", note: "Across six projects and two cross-project workflows" },
  { value: `${portfolio.implemented} / ${portfolio.tasks}`, label: "tasks implemented", note: `${portfolio.planned} planned evaluations remain` },
  { value: String(portfolio.headroom), label: "tasks with headroom", note: "Able to measure useful skill judgment" },
  { value: `${portfolio.maintainerReviewed} / ${portfolio.skills}`, label: "maintainer reviewed", note: "The portfolio’s clearest promotion gate" },
];

const attention = [
  { number: "01", title: "Maintainer review", detail: "Every published skill is awaiting owning-project review.", href: "skills/" },
  { number: "02", title: "Coverage gaps", detail: `${portfolio.planned} planned evaluations still need implementation and calibration.`, href: "evaluations/" },
  { number: "03", title: "Real-world evidence", detail: `${portfolio.maintainerIncidents} tasks currently originate from maintainer incidents.`, href: "methodology/" },
];

function coverageTone(implemented: number, total: number) {
  if (total === 0) return "empty";
  if (implemented === total) return "full";
  if (implemented > 0) return "partial";
  return "empty";
}

export default function Home() {
  return (
    <main>
      <SiteHeader active="overview" />

      <section className="hero" id="top">
        <div className="hero-copy">
          <Eyebrow>Portfolio health · current catalog</Eyebrow>
          <h1>Continuous evidence<br />for every UXL skill.</h1>
          <p className="lede">
            A vendor-neutral view of quality, evaluation coverage, ownership, and
            promotion readiness across the UXL Foundation project ecosystem.
          </p>
        </div>
        <aside className="hero-brief" aria-label="Portfolio status">
          <div className="status-line"><span className="pulse" aria-hidden="true" /><strong>Portfolio validation passing</strong></div>
          <p>The catalog is released. All eight skills remain in pilot or incubation while maintainer review and promotion evidence progress.</p>
          <a href="#portfolio">Review project health ↓</a>
        </aside>
      </section>

      <section className="summary" aria-label="Portfolio summary">
        {summary.map((item) => (
          <div className="metric" key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
            <small>{item.note}</small>
          </div>
        ))}
      </section>

      <section className="attention section-pad" aria-labelledby="attention-title">
        <div className="section-heading compact">
          <div><p className="section-label">Needs attention</p><h2 id="attention-title">The next decisions are visible.</h2></div>
          <p>Health is more than a pass rate. Ownership, evidence quality, source freshness, and missing evaluations determine whether a skill can be promoted.</p>
        </div>
        <div className="attention-grid">
          {attention.map((item) => (
            <a className="attention-card" href={item.href} key={item.number}>
              <span>{item.number}</span><h3>{item.title}</h3><p>{item.detail}</p><b>Inspect →</b>
            </a>
          ))}
        </div>
      </section>

      <section className="portfolio section-pad" id="portfolio">
        <div className="section-heading">
          <div><p className="section-label">Project portfolio</p><h2>One standard.<br />Project-level accountability.</h2></div>
          <p>Coverage counts are generated from the catalog and Harbor suite manifest. “Headroom” means an evaluation can distinguish useful judgment; it is not a library performance score.</p>
        </div>
        <div className="portfolio-table" role="table" aria-label="UXL skill portfolio health">
          <div className="portfolio-row portfolio-head" role="row">
            <span>Project skill</span><span>Maturity</span><span>Coverage</span><span>Evidence</span><span>Review</span><span>Next action</span>
          </div>
          {skills.map((skill) => {
            const stats = skillStats(skill);
            return (
              <a className="portfolio-row" href={`skills/#${skill.name}`} role="row" key={skill.name}>
                <span><b>{skill.displayName}</b><small>{sourceFreshness(skill)}</small></span>
                <span><StatusPill tone={skill.status === "pilot" ? "planned" : "neutral"}>{skill.status}</StatusPill></span>
                <span><b>{stats.implemented} / {skill.targetTaskCount}</b><small>{stats.planned} planned</small></span>
                <span><b>{stats.headroom} headroom</b><small>{stats.quality}</small></span>
                <span><StatusPill tone="watch">needed</StatusPill></span>
                <span><b>{stats.nextAction}</b><i aria-hidden="true">→</i></span>
              </a>
            );
          })}
        </div>
        <div className="table-legend">
          <span><i className="legend-dot full" />Implemented coverage</span>
          <span><i className="legend-dot partial" />Partial coverage</span>
          <span><i className="legend-dot empty" />No implemented coverage</span>
        </div>
      </section>

      <section className="capability section-pad" aria-labelledby="capability-title">
        <div className="section-heading inverse">
          <div><p className="section-label">Capability coverage</p><h2 id="capability-title">What each skill<br />is expected to teach.</h2></div>
          <p>Every project is evaluated against the same five behavioral classes while retaining project-specific tasks and verifiers.</p>
        </div>
        <div className="heatmap" role="table" aria-label="Implemented evaluation coverage by capability">
          <div className="heatmap-row heatmap-head" role="row">
            <span>Skill</span>{capabilityClasses.map((name) => <span key={name}>{name}</span>)}
          </div>
          {skills.map((skill) => (
            <a className="heatmap-row" href={`skills/#${skill.name}`} role="row" key={skill.name}>
              <span>{skill.displayName}</span>
              {capabilityClasses.map((name) => {
                const cell = capabilityCoverage(skill, name);
                return <span className={`coverage-cell ${coverageTone(cell.implemented, cell.total)}`} key={name}><b>{cell.implemented}</b><small>/{cell.total}</small></span>;
              })}
            </a>
          ))}
        </div>
      </section>

      <section className="evidence-path section-pad">
        <div className="section-heading compact">
          <div><p className="section-label">Evidence path</p><h2>From instruction to accepted result.</h2></div>
          <p>Managers see the status; members can move from a project to the exact evaluation contract and reviewable source.</p>
        </div>
        <ol className="path-steps">
          <li><span>01</span><h3>Current guidance</h3><p>Official sources, limitations, and intended behavior are recorded with the skill.</p><a href="skills/">Explore skills →</a></li>
          <li><span>02</span><h3>Behavior tested</h3><p>Tasks exercise correctness, selection, integration, debugging, and performance judgment.</p><a href="evaluations/">Inspect evaluations →</a></li>
          <li><span>03</span><h3>Matched comparison</h3><p>No-skill, previous-skill, and candidate-skill arms share the same task and environment.</p><a href="methodology/">Read the method →</a></li>
          <li><span>04</span><h3>Portable evidence</h3><p>Hosted and specialized systems return the same result and provenance contract.</p><a href="platforms/">See platforms →</a></li>
        </ol>
      </section>

      <section className="platform-preview section-pad">
        <div>
          <p className="section-label">Platform evidence</p>
          <h2>Hardware is a dimension,<br />not the headline.</h2>
          <p>Most evaluations run on hosted infrastructure. When a task genuinely depends on a device, backend, topology, or driver, any approved machine can plug into the same evidence contract.</p>
        </div>
        <div className="platform-preview-card">
          <StatusPill tone="good">Qualification evidence retained</StatusPill>
          <strong>{portfolio.targetQualifications} specialized lane record{portfolio.targetQualifications === 1 ? "" : "s"}</strong>
          <p>Each retained record is tied to one task, revision, lane, and expiry policy. It does not establish vendor preference or skill benefit.</p>
          <a href="platforms/">Review the neutral platform matrix →</a>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
