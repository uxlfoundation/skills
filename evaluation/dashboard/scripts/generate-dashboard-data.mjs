import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const dashboardRoot = fileURLToPath(new URL("..", import.meta.url));
const repositoryRoot = resolve(dashboardRoot, "../..");
const catalogPath = resolve(repositoryRoot, "skills.yaml");
const suitesPath = resolve(repositoryRoot, "evaluation/harbor/suites.json");
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

const [catalogSource, suitesSource] = await Promise.all([
  readFile(catalogPath, "utf8"),
  readFile(suitesPath, "utf8"),
]);
const catalog = parseCatalog(catalogSource);
const suites = JSON.parse(suitesSource);
const suitesBySkill = new Map(suites.suites.map((suite) => [suite.skill, suite]));

const dashboardData = {
  schemaVersion: "1.0",
  catalogStatus: catalog.catalogStatus,
  policy: suites.policy,
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
      tasks: suite.tasks,
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
