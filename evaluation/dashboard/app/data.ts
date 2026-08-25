import dashboardData from "./dashboard-data.json";

export type Capability = {
  id: string;
  class: string;
  description: string;
};

export type EvaluationTask = {
  name: string;
  status: string;
  role: string;
  calibration: string;
  track: string;
  environment: string;
  reproduction: string;
  origin: string;
  workflow: string[];
  hardware: string;
  covers: string[];
};

export type Skill = {
  name: string;
  displayName: string;
  ownerProject: string;
  ownerRepo: string;
  status: string;
  maintainerReview: string;
  lastSourceVerification: string | null;
  skillCard: string;
  sourceOfTruthTarget: string;
  targetTaskCount: number;
  capabilities: Capability[];
  tasks: EvaluationTask[];
};

export const skills = dashboardData.skills as Skill[];
export const policy = dashboardData.policy;
export const catalogStatus = dashboardData.catalogStatus;

export const allTasks = skills.flatMap((skill) =>
  skill.tasks.map((task) => ({ ...task, skill: skill.name, project: skill.displayName })),
);

export const portfolio = {
  skills: skills.length,
  tasks: allTasks.length,
  implemented: allTasks.filter((task) => task.status === "implemented").length,
  planned: allTasks.filter((task) => task.status === "planned").length,
  headroom: allTasks.filter((task) => task.calibration === "headroom").length,
  ceiling: allTasks.filter((task) => task.calibration === "ceiling").length,
  maintainerReviewed: skills.filter((skill) => skill.maintainerReview !== "needed").length,
  maintainerIncidents: allTasks.filter((task) => task.origin === "maintainer-incident").length,
};

export const capabilityClasses = policy.required_capability_classes as string[];

export function skillStats(skill: Skill) {
  const implemented = skill.tasks.filter((task) => task.status === "implemented").length;
  const planned = skill.tasks.filter((task) => task.status === "planned").length;
  const headroom = skill.tasks.filter((task) => task.calibration === "headroom").length;
  const ceiling = skill.tasks.filter((task) => task.calibration === "ceiling").length;
  const realWorld = skill.tasks.filter((task) => task.origin === "maintainer-incident").length;
  const quality = headroom >= 2 ? "Strong" : headroom === 1 ? "Developing" : "Needs evidence";
  const nextAction = planned > 0
    ? `${planned} planned evaluation${planned === 1 ? "" : "s"}`
    : skill.maintainerReview === "needed"
      ? "Schedule maintainer review"
      : "Maintain accepted evidence";
  return { implemented, planned, headroom, ceiling, realWorld, quality, nextAction };
}

export function capabilityCoverage(skill: Skill, capabilityClass: string) {
  const capabilityIds = new Set(
    skill.capabilities.filter((capability) => capability.class === capabilityClass).map((capability) => capability.id),
  );
  const relevant = skill.tasks.filter((task) => task.covers.some((id) => capabilityIds.has(id)));
  const implemented = relevant.filter((task) => task.status === "implemented").length;
  return { implemented, total: relevant.length };
}

export function titleCase(value: string) {
  return value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function sourceFreshness(skill: Skill) {
  return skill.lastSourceVerification ?? "Not recorded";
}

export function githubSkillUrl(skill: Skill) {
  return `https://github.com/uxlfoundation/skills/blob/main/${skill.skillCard}`;
}
