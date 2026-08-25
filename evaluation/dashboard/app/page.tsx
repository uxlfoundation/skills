const summary = [
  { value: "8", label: "UXL skills" },
  { value: "51", label: "evaluation tasks" },
  { value: "39", label: "implemented" },
  { value: "1.0", label: "GPU oracle reward" },
];

const skills = [
  { name: "oneTBB", coverage: "7 / 7", signal: "2 headroom", status: "incubating" },
  { name: "oneDNN", coverage: "5 / 6", signal: "1 headroom", status: "incubating" },
  { name: "oneDAL", coverage: "5 / 6", signal: "1 headroom", status: "incubating" },
  { name: "oneDPL", coverage: "4 / 6", signal: "1 headroom", status: "incubating" },
  { name: "oneMath", coverage: "3 / 6", signal: "1 headroom", status: "pilot" },
  { name: "oneCCL", coverage: "4 / 6", signal: "2 headroom", status: "incubating" },
  { name: "SYCL build + debug", coverage: "7 / 8", signal: "1 headroom", status: "incubating" },
  { name: "Performance validation", coverage: "4 / 6", signal: "proof needed", status: "incubating" },
];

const lanes = [
  { label: "GitHub-hosted CPU", detail: "Portable correctness and integration", state: "Active" },
  { label: "Hosted toolchain", detail: "Pinned SYCL compiler and runtime", state: "Active" },
  { label: "Windows/WSL Intel GPU", detail: "Arc B580 · /dev/dxg · Level Zero", state: "Qualified" },
  { label: "Distributed target", detail: "oneCCL topology and worker evidence", state: "Planned" },
];

export default function Home() {
  return (
    <main>
      <nav>
        <a className="brand" href="#top" aria-label="UXL evaluator home">UXL<span>/</span>EVAL</a>
        <div className="nav-links">
          <a href="#coverage">Coverage</a>
          <a href="#lanes">Runners</a>
          <a href="#evidence">Evidence</a>
          <a className="source-link" href="https://github.com/uxlfoundation/skills">View source ↗</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow"><span /> UXL evaluator control room</div>
        <h1>Evidence you can<br />route to real hardware.</h1>
        <p className="lede">
          One view of skill quality, execution coverage, and specialized runner
          readiness across the UXL Foundation library ecosystem.
        </p>
        <div className="hero-status">
          <div className="pulse" aria-hidden="true" />
          <div>
            <strong>Windows/WSL Intel GPU lane qualified</strong>
            <span>Immutable evaluator · Intel Arc · Harbor oracle passed</span>
          </div>
        </div>
      </section>

      <section className="summary" aria-label="Evaluator summary">
        {summary.map((item) => (
          <div className="metric" key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </div>
        ))}
      </section>

      <section className="route">
        <div>
          <p className="section-label">Execution topology</p>
          <h2>One evidence contract.<br />Multiple execution lanes.</h2>
        </div>
        <div className="route-line" aria-label="Evaluation execution flow">
          <div><small>01</small><b>Reviewed commit</b><span>Tasks, skills, verifiers</span></div>
          <i aria-hidden="true" />
          <div><small>02</small><b>Matched execution</b><span>Hosted or target hardware</span></div>
          <i aria-hidden="true" />
          <div><small>03</small><b>Retained evidence</b><span>Reward, trajectory, provenance</span></div>
        </div>
      </section>

      <section className="coverage" id="coverage">
        <div className="section-head">
          <div><p className="section-label">Portfolio coverage</p><h2>Built to measure judgment,<br />not keyword recall.</h2></div>
          <p>Implemented tasks span correctness, selection, integration, debugging, and performance. Promotion requires matched trials and maintainer review.</p>
        </div>
        <div className="skill-table" role="table" aria-label="UXL skill evaluation coverage">
          <div className="skill-row table-head" role="row"><span>Skill</span><span>Implemented</span><span>Evaluator signal</span><span>Status</span></div>
          {skills.map((skill, index) => (
            <div className="skill-row" role="row" key={skill.name}>
              <span><em>{String(index + 1).padStart(2, "0")}</em>{skill.name}</span>
              <span>{skill.coverage}</span><span>{skill.signal}</span><span>{skill.status}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="lanes" id="lanes">
        <div className="section-head inverse">
          <div><p className="section-label">Runner fabric</p><h2>Use ordinary compute<br />until the evidence needs more.</h2></div>
          <p>Portable tasks stay on hosted infrastructure. Device, topology, and driver-dependent work routes to controlled machines through private dispatch.</p>
        </div>
        <div className="lane-list">
          {lanes.map((lane) => (
            <div className="lane" key={lane.label}>
              <div className={`lane-state ${lane.state.toLowerCase()}`}><span />{lane.state}</div>
              <h3>{lane.label}</h3><p>{lane.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="evidence" id="evidence">
        <div className="evidence-title">
          <p className="section-label">Latest hardware proof</p>
          <h2>Intel GPU oracle<br />passed end to end.</h2>
          <a href="https://github.com/uxlfoundation/skills/pull/6">Review infrastructure PR ↗</a>
        </div>
        <div className="proof">
          <div className="proof-mark">PASS</div>
          <dl>
            <div><dt>Evaluator</dt><dd>f3481bb</dd></div>
            <div><dt>Interface</dt><dd>/dev/dxg</dd></div>
            <div><dt>Runtime</dt><dd>Level Zero GPU</dd></div>
            <div><dt>Workload</dt><dd>Compiled SYCL kernel</dd></div>
            <div><dt>Harbor reward</dt><dd>1.000</dd></div>
            <div><dt>Evidence</dt><dd>Retained privately</dd></div>
          </dl>
        </div>
      </section>

      <section className="done">
        <p className="section-label">Definition of done</p>
        <h2>A skill is ready when ownership,<br />behavior, and evidence agree.</h2>
        <ol>
          <li><span>01</span><b>Maintainer owned</b><p>Current sources, reviewed limitations, clear project home.</p></li>
          <li><span>02</span><b>Behavior proven</b><p>Five matched attempts per arm and a meaningful negative control.</p></li>
          <li><span>03</span><b>Hardware honest</b><p>Every target-specific claim carries environment provenance.</p></li>
          <li><span>04</span><b>Easy to consume</b><p>Clean installation to one verified result in ten minutes.</p></li>
        </ol>
      </section>

      <footer><div className="brand">UXL<span>/</span>EVAL</div><p>Public scorecard. Detailed trajectories and machine evidence remain access-controlled.</p><a href="#top">Back to top ↑</a></footer>
    </main>
  );
}
