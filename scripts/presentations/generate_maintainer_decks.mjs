import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "../..");
const skillDir = process.env.UXL_PRESENTATION_SKILL_DIR;
const pythonExecutable = process.env.UXL_PRESENTATION_PYTHON;
const runtimeNodeModules = process.env.UXL_PRESENTATION_NODE_MODULES;

if (!path.isAbsolute(skillDir ?? "") || !path.isAbsolute(pythonExecutable ?? "") || !path.isAbsolute(runtimeNodeModules ?? "")) {
  throw new Error("Set UXL_PRESENTATION_SKILL_DIR, UXL_PRESENTATION_PYTHON, and UXL_PRESENTATION_NODE_MODULES to absolute bundled-runtime paths.");
}

process.env.RUNTIME_NODE_MODULES = runtimeNodeModules;

const { FileBlob, PresentationFile } = await import(pathToFileURL(
  path.join(runtimeNodeModules, "@oai/artifact-tool/dist/artifact_tool.mjs"),
).href);

const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools/artifact_tool_utils.mjs"),
).href);

const sourceDir = path.join(repoRoot, "docs/maintainer-review/deck-source");
const screenshotDir = process.env.UXL_DECK_SCREENSHOT_DIR || path.join(repoRoot, ".codex/deck-build/screenshots");
const outputDir = path.join(repoRoot, "evaluation/dashboard/public/decks");
const stagingRoot = path.join(repoRoot, ".codex/deck-finalize");
const expectedSlideSizeEmu = "12192000,6858000";

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(stagingRoot, { recursive: true });

const ids = {
  project: {
    titles: ["sh/547294r6", "sh/9072xkry", "sh/cza94vmx", "sh/1cj2d8b6", "sh/dgbulwnm", "sh/yhg7epsj", "sh/cb2tkvap"],
    bodies: ["sh/k3yl0zql", "sh/ozy1ofad", "sh/d0jax03i", "sh/0ba143al", "sh/cf2tcr61", "sh/zi98nu94", "sh/dcbud0ra"],
    notes: ["nt/y90nupkv", "nt/hwbqtkby", "nt/ofy9wn61", "nt/jyx0ra1s", "nt/i107q5of", "nt/x8f69ofe", "nt/gnmp4jqx"],
  },
};

const projectDeckSourceSlides = [1, 3, 4, 5, 6, 7];
const projectDeckSourceIndexes = projectDeckSourceSlides.map((slideNumber) => slideNumber - 1);

const crossProjectDecks = [
  {
    slug: "uxl-sycl-build-debug-maintainer-briefing",
    skill: "uxl-sycl-build-debug",
    slides: [
      ["UXL SKILLS EVALUATOR\nSYCL Build & Debug Skill", "Portable build and runtime triage across UXL projects\nSeptember 2026 · 8 of 8 evaluation tasks implemented"],
      ["What the skill tells an agent today", "\u00A0Classify the failing phase — Configure, compile, link, runtime load, or device selection.\n\u00A0Record a reproducible environment — Include toolchain versions, target, commands, first error, and a safe local probe.\n\u00A0Prove the selected device — Enumerate it and run a minimal workload before blaming a library.\n\u00A0Check compile-time and runtime paths separately — CMake cache, link targets, loader paths, and plugins can fail independently.\n\u00A0Verify current support upstream — The skill does not embed a permanent backend matrix."],
      ["Evaluation inventory: all 8 tasks implemented", "\u00A0Device and runtime — Windows/WSL discovery, loader/plugin mismatch, and silent CPU fallback.\n\u00A0Build contracts — Compiler cache, backend link, compile-time backend selection, and transitive target linking.\n\u00A0Runtime composition — oneDNN plus threading-runtime integration.\n\u00A0What remains — Maintainer ownership and matched evidence across representative toolchains, not more task-count filling."],
      ["How we chose the content", "\u00A0Project-owned sources — SYCL toolchain docs plus UXL library build, example, test, and incident evidence.\n\u00A0Failure-shaped coverage — Each task starts at a boundary maintainers repeatedly diagnose.\n\u00A0Portable checks — Verifiers test observed build/runtime behavior rather than vendor names.\n\u00A0Honest limits — Specialized hardware enters only when hosted systems cannot reproduce the task faithfully."],
      ["What shared ownership would look like", "\u00A0UXL working-group reviewers own — Shared terminology, routing rules, safe probes, and vendor-neutral limitations.\n\u00A0Project maintainers validate hand-offs — Each library confirms where general SYCL triage ends and project behavior begins.\n\u00A0Toolchain owners refresh sources — Compiler, loader, plugin, and package changes update the source ledger and affected tasks.\n\u00A0UXL infrastructure maintains — Validators, Harbor execution, dashboards, and specialized-lane contracts."],
      ["A focused 30-minute maintainer review", "\u00A01. Confirm the five-phase triage model — Configure, compile, link, runtime load, device selection.\n\u00A02. Correct one routing boundary — Identify advice that belongs in a library-specific skill instead.\n\u00A03. Judge the eight tasks — Mark smoke coverage versus tasks worth matched model trials.\n\u00A04. Name a shared reviewer — One person or small working-group team is enough.\n\u00A0Outcome — A common first-response playbook that produces reproducible reports across UXL projects."],
    ],
  },
  {
    slug: "uxl-performance-validation-maintainer-briefing",
    skill: "uxl-performance-validation",
    slides: [
      ["UXL SKILLS EVALUATOR\nPerformance Validation Skill", "Correctness-first benchmark and claim discipline across UXL projects\nSeptember 2026 · 4 of 6 evaluation tasks implemented"],
      ["What the skill tells an agent today", "\u00A0Write the user-visible correctness contract first — Outputs, metrics, tolerances, and failure criteria.\n\u00A0Choose the baseline and scope — State exactly which work each timing includes.\n\u00A0Warm up and repeat — Report distribution and variance, not a single best run.\n\u00A0Synchronize asynchronous work — Host timers stop only after the measured operation completes.\n\u00A0Profile after a validated regression — Profilers explain a measured problem; they do not create one."],
      ["Evaluation inventory: 4 implemented, 2 target gaps", "\u00A0Implemented — Tiny async GPU claim; benchmark report repair; floating-reduction tolerance; cgroup concurrency quota.\n\u00A0Incident evidence — The concurrency task is grounded in a oneTBB maintainer incident.\n\u00A0Planned — Transfer-inclusive comparison and profile-after-regression on declared target lanes.\n\u00A0What this proves — Current tasks test evidence discipline; none yet retains measured skill headroom for promotion."],
      ["How we chose the content", "\u00A0Project-native benchmarks first — Each library's tests and benchmark tools remain authoritative.\n\u00A0Cross-project invariants — Correctness, baseline, scope, synchronization, variance, provenance, and claim language recur everywhere.\n\u00A0Adversarial scenarios — Tasks target tempting but invalid conclusions, not just command recall.\n\u00A0Visible gaps — Target-dependent measurement remains planned until qualified lanes and authentic regressions exist."],
      ["What shared ownership would look like", "\u00A0Working-group reviewers own — The common evidence and claim contract.\n\u00A0Project benchmark owners supply — Approved commands, metrics, tolerances, representative sizes, and interpretation limits.\n\u00A0Hardware owners qualify lanes — They prove the environment, not the skill's value.\n\u00A0UXL infrastructure maintains — Matched evaluation cells, provenance schemas, Harbor artifacts, and public dashboards."],
      ["A focused 30-minute maintainer review", "\u00A01. Confirm the evidence order — Correctness, baseline, scope, repetitions, variance, then profiling.\n\u00A02. Correct one benchmark assumption — Add a project-specific limitation or required metric.\n\u00A03. Judge the six tasks — Keep, rewrite, or remove; nominate an authentic regression with headroom.\n\u00A04. Name a shared owner — Include project benchmark owners in periodic review.\n\u00A0Outcome — Agents produce reproducible, narrowly scoped evidence before making performance claims."],
    ],
  },
];

function replaceText(presentation, id, oldText, newText) {
  presentation.resolve(id).text.replace(oldText, newText);
}

function setShapeText(presentation, id, text) {
  presentation.resolve(id).text = text;
}

function renumberSlideFooters(presentation) {
  for (const [index, slide] of presentation.slides.items.entries()) {
    if (index === 0) continue;
    for (const shape of slide.shapes.items) {
      const current = shape.text?.toString?.() ?? "";
      if (/^\s*\d+\s*$/.test(current)) shape.text.replace(current, String(index + 1));
    }
  }
}

async function replaceImage(presentation, id, imagePath, alt) {
  const image = presentation.resolve(id);
  const frame = image.frame;
  const crop = image.crop;
  const fit = image.fit;
  const geometry = image.geometry;
  const borderRadius = image.borderRadius;
  const rotation = image.rotation;
  const flipHorizontal = image.flipHorizontal;
  const flipVertical = image.flipVertical;
  const lockAspectRatio = image.lockAspectRatio;
  const bytes = new Uint8Array(await fs.readFile(imagePath));
  image.replace({ blob: bytes, contentType: "image/png", alt, ...(fit ? { fit } : {}) });
  image.frame = frame;
  image.crop = crop;
  image.geometry = geometry;
  image.borderRadius = borderRadius;
  image.rotation = rotation;
  image.flipHorizontal = flipHorizontal;
  image.flipVertical = flipVertical;
  image.lockAspectRatio = lockAspectRatio;
}

async function importDeck(templatePath) {
  return PresentationFile.importPptx(await FileBlob.load(templatePath));
}

async function finalizeDeck(presentation, templatePath, slug, slideCount, requiredTemplateReferenceSlides = Array.from({ length: slideCount }, (_, index) => index + 1)) {
  const stageDir = path.join(stagingRoot, slug);
  const finalPath = path.join(outputDir, `${slug}.pptx`);
  const candidatePath = path.join(stageDir, "candidate.pptx");
  const receiptPath = path.join(stagingRoot, "receipts", `${slug}.validation.json`);
  await fs.mkdir(stageDir, { recursive: true });
  await fs.mkdir(path.dirname(receiptPath), { recursive: true });
  await fs.rm(finalPath, { force: true });
  await fs.rm(receiptPath, { force: true });
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const referenceSha256 = crypto.createHash("sha256").update(await fs.readFile(templatePath)).digest("hex");

  await finalizePresentation({
    workspaceDir: repoRoot,
    candidatePath,
    finalPath,
    pythonExecutable,
    integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", expectedSlideSizeEmu,
      "--validate-bullet-geometry",
      "--validate-heading-fit",
    ],
    explicitTotalSlideCount: slideCount,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    sourceTemplatePath: templatePath,
    requiredTemplateReferenceSlides,
    minimumTemplateCoverageRatio: 1,
    fontPolicy: {
      basis: "reference",
      families: ["Arial", "Lato"],
      referencePath: templatePath,
      referenceSha256,
    },
    expectedSlideSizeEmu,
    verifyArtifactToolImport: true,
    receiptPath,
  });
  return finalPath;
}

async function buildExistingProjectDeck(slug) {
  const templatePath = path.join(sourceDir, `${slug}-template.pptx`);
  const presentation = await importDeck(templatePath);
  const projectName = slug.replace(/^uxl-/, "").replace(/-maintainer-briefing$/, "");
  const displayNames = { onednn: "oneDNN", onemath: "oneMath", onedal: "oneDAL", onetbb: "oneTBB", onedpl: "oneDPL", oneccl: "oneCCL" };
  const displayName = displayNames[projectName];
  replaceText(presentation, ids.project.titles[0], `${displayName} Skills`, `${displayName} Skill`);
  const subtitle = presentation.resolve(ids.project.bodies[0]);
  subtitle.text.replace("Maintainer briefing ·", "September 2026 ·");
  presentation.slides.remove(1);
  renumberSlideFooters(presentation);
  return finalizeDeck(presentation, templatePath, slug, 6, projectDeckSourceSlides);
}

async function buildCrossProjectDeck(deck) {
  const templatePath = path.join(sourceDir, "uxl-onednn-maintainer-briefing-template.pptx");
  const presentation = await importDeck(templatePath);
  for (let index = 0; index < deck.slides.length; index += 1) {
    const sourceIndex = projectDeckSourceIndexes[index];
    setShapeText(presentation, ids.project.titles[sourceIndex], deck.slides[index][0]);
    setShapeText(presentation, ids.project.bodies[sourceIndex], deck.slides[index][1]);
    presentation.resolve(ids.project.notes[sourceIndex]).setText([
      "[Sources]",
      `- https://github.com/uxlfoundation/skills/tree/main/skills/${deck.skill}`,
      `- https://github.com/uxlfoundation/skills/blob/main/skill-cards/${deck.skill}.md`,
      `- https://github.com/uxlfoundation/skills/blob/main/docs/maintainer-review/${deck.skill}.md`,
      "- https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/suites.json",
      "- https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATOR_POLICY.md",
      "[/Sources]",
      "",
      `Speaker cue: ${deck.slides[index][0].replace(/\n/g, ": ")}`,
    ].join("\n"));
  }
  presentation.slides.remove(1);
  renumberSlideFooters(presentation);
  return finalizeDeck(presentation, templatePath, deck.slug, 6, projectDeckSourceSlides);
}

async function buildOverview() {
  const templatePath = path.join(sourceDir, "uxl-skills-maintainer-overview-template.pptx");
  const presentation = await importDeck(templatePath);
  replaceText(presentation, "sh/k3yl0zql", "Maintainer overview · August 2026", "Maintainer overview · September 2026");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0Do you test every model, harness, and version? — No. We select representative, risk-based cells and publish the untested gaps.", "\u00A0Do you test every combination? — No. We publish representative, risk-based cells and the gaps.");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0What happens when a model, harness, or toolchain changes? — Re-run the affected cells; older results remain historical evidence, not current proof.", "\u00A0What changes invalidate evidence? — Re-run affected cells; older results remain history, not current proof.");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0Could a skill overfit the evaluator? — Use maintainer incidents, hidden implementation-neutral checks, negative controls, multiple tasks, and trajectory review.", "\u00A0How do you limit overfitting? — Maintainer incidents, hidden checks, negative controls, multiple tasks, and trajectory review.");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0What if every arm passes? — Classify the task as ceiling/smoke; do not claim quality lift and seek a harder task.", "\u00A0What if every arm passes? — Keep it as smoke coverage; claim no lift and seek a harder task.");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0Does a hardware oracle prove the skill helps? — No. It qualifies the execution lane; matched model trials are a separate experiment.", "\u00A0Does hardware qualification prove skill value? — No. Qualification and matched skill trials are separate gates.");
  replaceText(presentation, "sh/cbu58j2h", "\u00A0Can we compare scores across cells? — Look for consistent conclusions and report exceptions; never pool incompatible models or environments into one universal score.", "\u00A0Can scores be pooled? — No universal score; report conclusions within each model, harness, software, and environment cell.");
  await replaceImage(presentation, "im/lwn2dc3m", path.join(screenshotDir, "overview.png"), "UXL Skills Evaluator overview dashboard");
  await replaceImage(presentation, "im/axovit03", path.join(screenshotDir, "skills.png"), "UXL Skills Evaluator skill catalog");
  await replaceImage(presentation, "im/byxwryh8", path.join(screenshotDir, "evaluations.png"), "UXL Skills Evaluator evaluation explorer");
  await replaceImage(presentation, "im/ixcj6lgb", path.join(screenshotDir, "methodology.png"), "UXL Skills Evaluator methodology page");
  await replaceImage(presentation, "im/2lcz2l0n", path.join(screenshotDir, "platforms.png"), "UXL Skills Evaluator platform evidence page");
  return finalizeDeck(presentation, templatePath, "uxl-skills-maintainer-overview", 14);
}

async function buildTargetGuide() {
  const templatePath = path.join(sourceDir, "uxl-specialized-target-onboarding-template.pptx");
  const presentation = await importDeck(templatePath);
  setShapeText(presentation, "sh/nu58f2hs", "Public task +\ntarget adapter");
  setShapeText(presentation, "sh/bip8jmho", "Target integration changes; the evidence contract does not.");
  replaceText(presentation, "sh/0ba143al", "\u00A0Platform adapter — Add scripts/runner/run-<platform>-oracle.sh to verify the source SHA, probe the host, map the device, run Harbor, and enforce the oracle gate.", "\u00A0Target adapter — Configure target-adapter.json; the shared run_target_adapter.py verifies the SHA, probes the host, runs Harbor, and enforces the oracle gate.");
  replaceText(presentation, "sh/dcbud0ra", "\u00A0Windows/WSL option — Use start-ephemeral-wsl-runner.ps1 with the private repository and labels; native Linux follows GitHub's displayed registration commands.", "\u00A0Start or resume safely — Windows/WSL uses start-ephemeral-wsl-runner.ps1, which resumes a matching offline registration after reboot and refuses ambiguous state; native Linux may run the ephemeral agent directly.");
  const operator = presentation.resolve("sh/0b65obm9");
  operator.text.replace("\u00A0Preserve the evidence — From the Actions run, download the complete artifact ZIP before inspecting or cleaning the runner workspace.", "\u00A0Preserve the evidence — Download the complete artifact ZIP before inspecting or cleaning the runner workspace.");
  operator.text.replace("\u00A0Import it — python scripts/import_harbor_artifact.py <downloaded-artifact.zip>", "\u00A0Stage it — python scripts/import_harbor_artifact.py <artifact.zip>; review the sanitized qualification-record.json before publication.");
  setShapeText(presentation, "sh/cbu58j2h", "\u00A0Download — Keep the complete artifact ZIP intact; it carries provenance, results, trajectories, verifier output, configs, and probes.\n\u00A0Stage — Run python scripts/import_harbor_artifact.py <artifact.zip>; the importer checks hashes and stages a sanitized candidate.\n\u00A0Review — Check the public labels and limitations, then publish only qualification-record.json through normal review.\n\u00A0Audit — Inspect the task, verifier, trajectory, artifacts, configs, and provenance before accepting the lane.\n\u00A0Classify failures — Provisioning, network, driver, container, and runner failures are infrastructure failures, not skill failures.");
  replaceText(presentation, "sh/0f2lgnmp", "\u00A0Reviewable anywhere — The complete artifact imports into the standard Harbor viewers without platform-specific dashboard code.", "\u00A0Reviewable anywhere — Private logs stay access-controlled; the sanitized qualification record uses the shared dashboard and schema.");
  replaceText(presentation, "sh/0f2lgnmp", "\u00A0Owned and maintainable — A named platform owner keeps labels, probes, images, runtime guidance, and limitations current.", "\u00A0Owned and maintainable — A named lane owner keeps target-adapter.json, labels, probes, images, runtime guidance, and limitations current.");
  return finalizeDeck(presentation, templatePath, "uxl-specialized-target-onboarding", 12);
}

const generated = [];
generated.push(await buildOverview());
generated.push(await buildTargetGuide());
for (const slug of ["uxl-onednn-maintainer-briefing", "uxl-onemath-maintainer-briefing", "uxl-onedal-maintainer-briefing", "uxl-onetbb-maintainer-briefing", "uxl-onedpl-maintainer-briefing", "uxl-oneccl-maintainer-briefing"]) {
  generated.push(await buildExistingProjectDeck(slug));
}
for (const deck of crossProjectDecks) generated.push(await buildCrossProjectDeck(deck));

await fs.writeFile(path.join(outputDir, "manifest.json"), `${JSON.stringify({
  generatedFor: "2026-09-04",
  decks: generated.map((file) => path.basename(file)),
}, null, 2)}\n`);

for (const file of generated) console.log(path.relative(repoRoot, file));
