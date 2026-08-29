import { readFile, readdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { directoryDigest } from "./directory-digest.mjs";

const dashboardRoot = fileURLToPath(new URL("..", import.meta.url));
const repositoryRoot = resolve(dashboardRoot, "../..");
const catalogPath = resolve(repositoryRoot, "skills.yaml");
const suitesPath = resolve(repositoryRoot, "evaluation/harbor/suites.json");
const cellsRoot = resolve(repositoryRoot, "evaluation/harbor/results/cells");
const qualificationsRoot = resolve(repositoryRoot, "evaluation/harbor/results/qualifications");
const outputPath = resolve(dashboardRoot, "app/dashboard-data.json");

function parseCatalog(source) {
  const catalogStatus = source.match(/^catalog_status:\s*"([^"]+)"/m)?.[1];
  const skills = [];
  let current = null;

  for (const line of source.split(/\r?\n/)) {
    const skillStart = line.match(/^ {2}- name:\s*"([^"]+)"\s*$/);
    if (skillStart) {
      current = { name: skillStart[1] };
      skills.push(current);
      continue;
    }
    const field = line.match(/^ {4}([a-z_]+):\s*"([^"]*)"\s*$/);
    if (current && field) current[field[1]] = field[2];
  }

  if (!catalogStatus || skills.length === 0) {
    throw new Error("Unable to parse the catalog status or skill entries from skills.yaml");
  }
  for (const skill of skills) {
    for (const field of ["name", "status", "owner_project", "owner_repo", "skill_card", "maintainer_review"]) {
      if (!skill[field]) throw new Error(`Catalog skill ${skill.name ?? "<unknown>"} is missing ${field}`);
    }
  }
  return { catalogStatus, skills };
}

const [catalogSource, suitesSource, cellNames, qualificationNames] = await Promise.all([
  readFile(catalogPath, "utf8"),
  readFile(suitesPath, "utf8"),
  readdir(cellsRoot).catch(() => []),
  readdir(qualificationsRoot).catch(() => []),
]);
const catalog = parseCatalog(catalogSource);
const suites = JSON.parse(suitesSource);
const suitesBySkill = new Map(suites.suites.map((suite) => [suite.skill, suite]));
const evaluationCells = await Promise.all(
  cellNames
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map(async (name) => {
      const cell = JSON.parse(await readFile(resolve(cellsRoot, name), "utf8"));
      const [taskDigest, verifierDigest, candidateSkillDigest] = await Promise.all([
        directoryDigest(resolve(repositoryRoot, "evaluation/harbor/tasks", cell.scope.task)),
        directoryDigest(resolve(repositoryRoot, "evaluation/harbor/tasks", cell.scope.task, "tests")),
        directoryDigest(resolve(repositoryRoot, "skills", cell.scope.skill)),
      ]);
      const repositoryChanges = [];
      if (taskDigest !== cell.scope.task_revision.content_sha256) repositoryChanges.push("task");
      if (verifierDigest !== cell.scope.verifier_sha256) repositoryChanges.push("verifier");
      if (candidateSkillDigest !== cell.treatment.candidate_skill.content_sha256) repositoryChanges.push("candidate skill");
      return {
        id: cell.cell_id,
        stage: cell.stage,
        recordedAt: cell.recorded_at,
        skill: cell.scope.skill,
        task: cell.scope.task,
        model: cell.agent.model,
        agent: cell.agent.name,
        harness: cell.agent.harness,
        harnessVersion: cell.agent.harness_version,
        reasoningEffort: cell.agent.reasoning_effort,
        environment: cell.execution.environment,
        os: cell.execution.os,
        architecture: cell.execution.architecture,
        hardware: cell.execution.hardware.class,
        toolchain: cell.execution.toolchain,
        attemptsPerArm: cell.execution.attempts_per_arm,
        maxAgeDays: cell.freshness.max_age_days,
        repositoryStatus: repositoryChanges.length === 0 ? "matches" : "changed",
        repositoryChanges,
        rewards: Object.fromEntries(
          Object.entries(cell.results.arms).map(([arm, result]) => [arm, result.mean_reward]),
        ),
        source: `evaluation/harbor/results/cells/${name}`,
      };
    }),
);
evaluationCells.sort((left, right) => left.recordedAt.localeCompare(right.recordedAt) || left.id.localeCompare(right.id));
const targetQualifications = await Promise.all(
  qualificationNames
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map(async (name) => {
      const record = JSON.parse(await readFile(resolve(qualificationsRoot, name), "utf8"));
      const [taskDigest, verifierDigest] = await Promise.all([
        directoryDigest(resolve(repositoryRoot, "evaluation/harbor/tasks", record.scope.task)),
        directoryDigest(resolve(repositoryRoot, "evaluation/harbor/tasks", record.scope.task, "tests")),
      ]);
      const repositoryChanges = [];
      if (taskDigest !== record.scope.task_revision.content_sha256) repositoryChanges.push("task");
      if (verifierDigest !== record.scope.verifier_sha256) repositoryChanges.push("verifier");
      return {
        id: record.qualification_id,
        recordedAt: record.recorded_at,
        skill: record.scope.skill,
        task: record.scope.task,
        taskCommit: record.scope.task_revision.commit,
        laneId: record.lane.lane_id,
        adapterId: record.lane.adapter_id,
        displayName: record.lane.display_name,
        environment: record.lane.environment,
        hardwareClass: record.lane.hardware_class,
        vendor: record.lane.vendor,
        device: record.lane.device,
        interface: record.lane.interface,
        os: record.lane.os,
        architecture: record.lane.architecture,
        control: record.lane.control,
        maxAgeDays: record.freshness.max_age_days,
        workflowVisibility: record.evidence.workflow.visibility,
        repositoryStatus: repositoryChanges.length === 0 ? "matches" : "changed",
        repositoryChanges,
        limitations: record.limitations,
        source: `evaluation/harbor/results/qualifications/${name}`,
      };
    }),
);
targetQualifications.sort((left, right) => left.recordedAt.localeCompare(right.recordedAt) || left.id.localeCompare(right.id));

const dashboardData = {
  schemaVersion: "1.0",
  catalogStatus: catalog.catalogStatus,
  policy: suites.policy,
  evaluationCells,
  targetQualifications,
  skills: catalog.skills.map((catalogSkill) => {
    const suite = suitesBySkill.get(catalogSkill.name);
    if (!suite) throw new Error(`No Harbor suite found for ${catalogSkill.name}`);
    return {
      name: catalogSkill.name,
      displayName: catalogSkill.owner_project === "UXL cross-project"
        ? catalogSkill.name === "uxl-sycl-build-debug"
          ? "SYCL build + debug"
          : "Performance validation"
        : catalogSkill.owner_project,
      ownerProject: catalogSkill.owner_project,
      ownerRepo: catalogSkill.owner_repo,
      status: catalogSkill.status,
      maintainerReview: catalogSkill.maintainer_review,
      lastSourceVerification: catalogSkill.last_source_verification ?? null,
      skillCard: catalogSkill.skill_card,
      sourceOfTruthTarget: catalogSkill.source_of_truth_target,
      targetTaskCount: suite.target_task_count,
      capabilities: suite.capabilities,
      tasks: suite.tasks.map((task) => ({
        ...task,
        evaluationCells: evaluationCells.filter((cell) => cell.task === task.name),
      })),
    };
  }),
};

if (dashboardData.skills.length !== suites.suites.length) {
  throw new Error("skills.yaml and evaluation/harbor/suites.json do not contain the same number of skills");
}

const rendered = `${JSON.stringify(dashboardData, null, 2)}\n`;
if (process.argv.includes("--check")) {
  const current = await readFile(outputPath, "utf8").catch(() => "");
  if (current !== rendered) {
    console.error("Dashboard data is stale. Run npm run data:generate.");
    process.exit(1);
  }
  console.log("Dashboard data is current.");
} else {
  await writeFile(outputPath, rendered, "utf8");
  console.log(`Wrote ${outputPath}`);
}
