import { PageIntro, SiteFooter, SiteHeader } from "../components";
import { allTasks, portfolio, skills } from "../data";
import { EvaluationExplorer } from "./evaluation-explorer";

export const dynamic = "force-static";

const evaluationSummary = [
  [portfolio.implemented, "implemented"],
  [portfolio.headroom, "headroom"],
  [portfolio.ceiling, "ceiling / smoke"],
  [portfolio.planned, "planned"],
] as const;

export default function EvaluationsPage() {
  return (
    <main>
      <SiteHeader prefix="../" active="evaluations" />
      <PageIntro label="Evaluation explorer" title={<>See what is tested.<br />Inspect how it is judged.</>}>
        Search the complete task portfolio, separate implemented evidence from planned coverage, and open the exact task and verifier source.
      </PageIntro>
      <section className="mini-summary section-pad" aria-label="Evaluation summary">
        {evaluationSummary.map(([value, label]) => <div key={label}><strong>{value}</strong><span>{label}</span></div>)}
      </section>
      <section className="explorer-section section-pad">
        <EvaluationExplorer tasks={allTasks} projects={skills.map((skill) => skill.displayName)} />
      </section>
      <SiteFooter prefix="../" />
    </main>
  );
}
