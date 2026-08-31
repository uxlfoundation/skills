import { PageIntro, SiteFooter, SiteHeader } from "../components";
import { policy } from "../data";

export const dynamic = "force-static";

const evidenceStates = [
  ["Headroom", "Matched trials show that the task can distinguish useful skill judgment."],
  ["Ceiling", "All audited arms meet the quality bar; useful as smoke coverage, not proof of quality lift."],
  ["No lift", "The task has room to improve, but the candidate skill has not shown a durable advantage."],
  ["Manual", "The task requires a manually supplied environment or specialized system."],
  ["Uncalibrated", "No valid matched model screen has been accepted yet."],
];

export default function MethodologyPage() {
  return (
    <main>
      <SiteHeader prefix="../" active="methodology" />
      <PageIntro label="Evaluation methodology" title={<>Correctness first.<br />Claims after evidence.</>}>
        The evaluator measures agent behavior under controlled comparisons. It does not use hardware qualification, token savings, or a single successful run as a substitute for skill benefit.
      </PageIntro>

      <section className="method-steps section-pad">
        <article><span>01</span><h2>Qualify the task</h2><p>The oracle must earn full reward on the declared environment before model trials begin.</p></article>
        <article><span>02</span><h2>Match the arms</h2><p>{policy.comparison_arms.map((arm) => arm).join(", ")} receive the same task, revision, model, effort, and environment.</p></article>
        <article><span>03</span><h2>Verify quality</h2><p>Correctness and task reward gate all efficiency comparisons. Infrastructure failures are excluded and rerun unchanged.</p></article>
        <article><span>04</span><h2>Promote carefully</h2><p>Promotion requires five attempts per arm, current sources, clear limitations, and owning-project maintainer review.</p></article>
        <article><span>05</span><h2>Invalidate honestly</h2><p>Every accepted cell records the model, harness, software, task, skill, environment, and hardware dimensions that make its claim current. A material change marks the result stale; it does not rewrite history.</p></article>
      </section>

      <section className="definitions section-pad">
        <div className="section-heading compact">
          <div><p className="section-label">Evidence language</p><h2>Read every status consistently.</h2></div>
          <p>These labels describe evaluator evidence. They do not rate the health, quality, or performance of a UXL library.</p>
        </div>
        <div className="definition-list">
          {evidenceStates.map(([term, definition]) => <div key={term}><h3>{term}</h3><p>{definition}</p></div>)}
        </div>
      </section>

      <section className="policy-grid section-pad">
        <div><p className="section-label">Portfolio minimum</p><strong>{policy.minimum_tasks_per_skill}</strong><span>tasks per skill</span></div>
        <div><p className="section-label">Discriminating minimum</p><strong>{policy.minimum_discriminating_tasks_per_skill}</strong><span>tasks per skill</span></div>
        <div><p className="section-label">Promotion trials</p><strong>{policy.attempts.promotion}</strong><span>attempts per arm</span></div>
        <div><p className="section-label">Quality floor</p><strong>{policy.efficiency.verified_reward_floor.toFixed(1)}</strong><span>before efficiency</span></div>
      </section>

      <section className="method-cta section-pad">
        <div><p className="section-label">Reviewable by design</p><h2>Every public status should lead back to source.</h2><p>Skill guidance, task instructions, verifier code, coverage metadata, and accepted summaries live in the public repository. Raw trajectories and private-machine provenance remain access-controlled.</p></div>
        <div><a href="https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATOR_POLICY.md">Read evaluator policy ↗</a><a href="https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATION_CELL_CONTRACT.md">Read evidence-cell contract ↗</a><a href="https://github.com/uxlfoundation/skills/blob/main/docs/release-and-promotion-policy.md">Read promotion policy ↗</a></div>
      </section>
      <SiteFooter prefix="../" />
    </main>
  );
}
