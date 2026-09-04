import { PageIntro, SiteFooter, SiteHeader, StatusPill } from "../components";
import { capabilityCoverage, githubSkillUrl, maintainerDeckUrl, skillStats, skills, sourceFreshness, titleCase } from "../data";

export const dynamic = "force-static";

export default function SkillsPage() {
  return (
    <main>
      <SiteHeader prefix="../" active="skills" />
      <PageIntro label="Skill catalog" title={<>Eight skills.<br />Eight accountable portfolios.</>}>
        Each project view connects maturity, source freshness, capability coverage, evaluation evidence, and the next promotion action.
      </PageIntro>

      <section className="skill-index section-pad" aria-label="Skill index">
        {skills.map((skill) => {
          const stats = skillStats(skill);
          return (
            <a href={`#${skill.name}`} className="skill-index-card" key={skill.name}>
              <span>{skill.displayName}</span><b>{stats.implemented}/{skill.targetTaskCount}</b><small>{stats.headroom} headroom · {skill.status}</small>
            </a>
          );
        })}
      </section>

      <section className="skill-details section-pad">
        {skills.map((skill, index) => {
          const stats = skillStats(skill);
          return (
            <article className="skill-detail" id={skill.name} key={skill.name}>
              <header className="skill-detail-head">
                <div>
                  <span className="record-number">{String(index + 1).padStart(2, "0")} / {String(skills.length).padStart(2, "0")}</span>
                  <p className="section-label">{skill.ownerProject}</p>
                  <h2>{skill.displayName}</h2>
                  <div className="pill-row">
                    <StatusPill tone={skill.status === "pilot" ? "planned" : "neutral"}>{skill.status}</StatusPill>
                    <StatusPill tone="watch">maintainer review needed</StatusPill>
                    <StatusPill tone={stats.headroom > 0 ? "good" : "watch"}>{stats.headroom} headroom</StatusPill>
                  </div>
                </div>
                <div className="skill-score">
                  <strong>{stats.implemented}<small>/{skill.targetTaskCount}</small></strong>
                  <span>evaluations implemented</span>
                  <div className="progress-track"><i style={{ width: `${(stats.implemented / skill.targetTaskCount) * 100}%` }} /></div>
                </div>
              </header>

              <div className="skill-facts">
                <dl>
                  <div><dt>Evidence quality</dt><dd>{stats.quality}</dd></div>
                  <div><dt>Maintainer incidents</dt><dd>{stats.realWorld}</dd></div>
                  <div><dt>Source verification</dt><dd>{sourceFreshness(skill)}</dd></div>
                  <div><dt>Next action</dt><dd>{stats.nextAction}</dd></div>
                </dl>
                <div className="skill-links">
                  <a href={githubSkillUrl(skill)}>Read skill card ↗</a>
                  <a href={maintainerDeckUrl(skill, "pdf")}>Maintainer deck (PDF) ↓</a>
                  <a href={maintainerDeckUrl(skill, "pptx")}>Editable deck (PowerPoint) ↓</a>
                  <a href={skill.ownerRepo}>Owning project ↗</a>
                </div>
              </div>

              <div className="capability-cards">
                {skill.capabilities.map((capability) => {
                  const coverage = capabilityCoverage(skill, capability.class);
                  return (
                    <div className="capability-card" key={capability.id}>
                      <span>{titleCase(capability.class)}</span>
                      <b>{coverage.implemented}/{coverage.total}</b>
                      <p>{capability.description}</p>
                    </div>
                  );
                })}
              </div>

              <div className="skill-task-list">
                <div className="task-list-head"><span>Evaluation</span><span>Role</span><span>Evidence</span><span>Environment</span></div>
                {skill.tasks.map((task) => (
                  <a href={`../evaluations/#${task.name}`} className="task-list-row" key={task.name}>
                    <span><b>{task.name}</b><small>{task.status}</small></span>
                    <span>{task.role}</span><span>{task.calibration}</span><span>{titleCase(task.environment)}</span>
                  </a>
                ))}
              </div>
              <a className="back-link" href="#top">Back to skill index ↑</a>
            </article>
          );
        })}
      </section>
      <SiteFooter prefix="../" />
    </main>
  );
}
