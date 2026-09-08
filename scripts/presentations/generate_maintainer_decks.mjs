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
const overviewDeckSourceSlides = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];

const projectPresenterConfigs = {
  onednn: {
    displayName: "oneDNN",
    coverage: "5 of 6 evaluation tasks are implemented",
    focus: "primitive and graph selection, memory descriptors and reorders, fusion parity, numeric checks, and benchdnn-based diagnosis",
    workflow: "start from operation semantics, make layouts explicit, compare primitive and graph paths, isolate reorder cost, and finish with a reproducible correctness check",
    inventory: "five runnable scenarios cover core integration risks; the remaining framework/regression scenario needs a more authentic fixture",
    sourceFocus: "official oneDNN documentation, examples, tests, and recurring descriptor, reorder, fusion, scratchpad, and blocked-layout failure boundaries",
  },
  onemath: {
    displayName: "oneMath",
    coverage: "3 of 6 evaluation tasks are implemented",
    focus: "domain and API choice, queue and dependency handling, backend dispatch, linking, storage, workspace, and reproducibility",
    workflow: "choose the computation model first, record backend and runtime details, respect storage and workspace contracts, and separate compile, link, runtime, and numeric failures",
    inventory: "three runnable scenarios establish smoke and evidence checks; RNG chaining, backend integration, and dispatch-overhead scenarios still need authentic project cases",
    sourceFocus: "official oneMath documentation, examples, tests, and maintainer evidence, with version-specific backend claims deferred to current upstream sources",
  },
  onedal: {
    displayName: "oneDAL",
    coverage: "5 of 6 evaluation tasks are implemented",
    focus: "native and scikit-learn-style APIs, host and distributed modes, table shape and orientation, result parity, conversion cost, and quality checks",
    workflow: "choose the interface and execution mode from the data and memory model, make table contracts explicit, compare outputs with a stated metric, and include conversion costs",
    inventory: "five runnable scenarios cover interface, data-contract, parity, and distributed concerns; the remaining quality-regression case needs a representative maintainer fixture",
    sourceFocus: "official oneDAL documentation, examples, tests, and failure boundaries around tables, distributed execution, conversion, and model-quality validation",
  },
  onetbb: {
    displayName: "oneTBB",
    coverage: "all 7 evaluation tasks are implemented",
    focus: "parallel patterns, partitioning and grain size, shared state, flow-graph bounds, arenas, cancellation, and exception behavior",
    workflow: "choose the parallel pattern before tuning, isolate mutable state, justify grain and partitioner choices with evidence, and validate cancellation and exception paths",
    inventory: "all seven scenarios are runnable, but task count is not evidence of skill benefit; maintainers should distinguish smoke coverage from genuinely discriminating cases",
    sourceFocus: "official oneTBB documentation, examples, tests, and incident-shaped cases involving oversubscription, unsafe state, flow control, cancellation, and exceptions",
  },
  onedpl: {
    displayName: "oneDPL",
    coverage: "4 of 6 evaluation tasks are implemented",
    focus: "host and device execution policies, iterator validity, data lifetime, synchronization, ordering, and toolchain/runtime boundaries",
    workflow: "select the execution policy and device deliberately, validate iterator and lifetime contracts, synchronize before observing results, and separate toolchain, runtime, and algorithm failures",
    inventory: "four hosted scenarios test portable contracts; two device-dependent gaps remain until a qualified target lane can exercise them without favoring a vendor",
    sourceFocus: "official oneDPL and SYCL documentation, examples, tests, and failure boundaries around policies, iterators, lifetime, synchronization, and fallback behavior",
  },
  oneccl: {
    displayName: "oneCCL",
    coverage: "5 of 7 evaluation tasks are implemented",
    focus: "collective contracts, rank agreement, operation ordering, counts and datatypes, completion waits, plugin selection, and rank-local diagnosis",
    workflow: "make every rank's contract explicit, capture rank-local evidence, wait for completion before reading results, and isolate API, version, transport, and plugin assumptions",
    inventory: "five runnable scenarios cover core collective contracts, including a real zero-count fixture; multi-node and device-dependent cases remain planned",
    sourceFocus: "official oneCCL documentation, examples, tests, and distributed failure evidence involving rank mismatch, ordering, completion, transport, and plugins",
  },
};

function projectPresenterNotes(config) {
  return [
    {
      purpose: `Introduce the draft ${config.displayName} skill and its current evaluation coverage.`,
      explain: `The skill helps coding agents reason about ${config.focus}.`,
      emphasize: "This is a UXL-authored starting point awaiting project review, not approved maintainer guidance.",
    },
    {
      purpose: "Walk through the behavior the skill asks an agent to follow today.",
      explain: `The intended sequence is to ${config.workflow}.`,
      emphasize: "A useful answer ends with reproducible evidence and a clear failure classification, not a plausible-looking command alone.",
    },
    {
      purpose: "Separate evaluation inventory from evidence that the skill improves outcomes.",
      explain: `${config.coverage}; ${config.inventory}.`,
      emphasize: "Implemented means the task can run. It does not mean the task passes, discriminates between treatments, or supports a promotion claim.",
    },
    {
      purpose: "Show how the draft guidance and task set were selected.",
      explain: `The starting material comes from ${config.sourceFocus}.`,
      emphasize: "Maintainers should correct, remove, or replace anything that does not reflect current project practice.",
    },
    {
      purpose: "Clarify the proposed ownership boundary.",
      explain: `${config.displayName} maintainers own triggers, API truth, source freshness, limitations, and authentic cases; UXL maintains the catalog, Harbor integration, comparison design, and dashboard.`,
      emphasize: "The skill cannot move beyond its incubating state without named project review.",
    },
    {
      purpose: "End with a small, concrete review request.",
      explain: "Ask maintainers to check the trigger and technical guidance, judge the task inventory, and name a reviewer or owner.",
      emphasize: "The desired output is specific corrections and realistic cases, not blanket endorsement of the draft.",
    },
  ];
}

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
    notes: [
      {
        purpose: "Introduce the shared SYCL build-and-debug skill and its current 8-of-8 runnable task inventory.",
        explain: "It gives agents a portable first-response method for failures that cross compiler, loader, runtime, device-selection, and library boundaries.",
        emphasize: "This shared skill complements project-specific guidance; it does not replace a library maintainer's diagnosis.",
      },
      {
        purpose: "Explain the five-phase triage path used by the skill.",
        explain: "Agents classify configure, compile, link, runtime-load, and device-selection failures separately, record the environment, and prove the selected device with a minimal workload.",
        emphasize: "The portable observation is authoritative; the skill deliberately avoids a permanent vendor or backend support matrix.",
      },
      {
        purpose: "Interpret the eight implemented tasks accurately.",
        explain: "The tasks cover discovery, loader and plugin mismatch, silent fallback, compiler cache, backend linking, compile-time selection, transitive targets, and runtime composition.",
        emphasize: "Complete task inventory is not the same as measured skill benefit; matched model and toolchain cells are still needed.",
      },
      {
        purpose: "Describe how the shared content was chosen.",
        explain: "The draft combines official toolchain and project sources with recurring failure boundaries, then verifies observed behavior rather than checking vendor names.",
        emphasize: "Specialized hardware is introduced only when hosted systems cannot reproduce a case faithfully.",
      },
      {
        purpose: "Set expectations for cross-project ownership.",
        explain: "Shared reviewers own terminology and safe probes; library maintainers validate hand-offs; toolchain owners refresh changing source facts; UXL operates evaluation infrastructure.",
        emphasize: "Every routing boundary needs an identifiable upstream owner so advice does not become stale or contradictory.",
      },
      {
        purpose: "Conclude with a focused review request.",
        explain: "Ask reviewers to confirm the five phases, correct one routing boundary, classify the eight tasks, and identify a shared owner.",
        emphasize: "Success is a common, reproducible first-response playbook—not universal approval of every draft sentence.",
      },
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
    notes: [
      {
        purpose: "Introduce the shared performance-validation skill and its current 4-of-6 runnable task inventory.",
        explain: "The skill teaches correctness-first benchmark and claim discipline that applies across UXL projects.",
        emphasize: "It does not replace each project's benchmark suite, approved metrics, or interpretation by performance owners.",
      },
      {
        purpose: "Explain the evidence order the skill expects.",
        explain: "Define correctness, baseline, and timing scope; warm up and repeat; synchronize asynchronous work; report variance; profile only after a regression is established.",
        emphasize: "A faster number is not useful unless the compared work and user-visible result are demonstrably equivalent.",
      },
      {
        purpose: "Interpret the implemented and planned evaluation tasks.",
        explain: "Four tasks exercise asynchronous timing, report repair, floating tolerance, and constrained concurrency; transfer-inclusive and profile-after-regression cases remain target-dependent gaps.",
        emphasize: "The current tasks test evidence discipline, but none yet supports a broad claim that the skill improves performance work.",
      },
      {
        purpose: "Describe the design principles behind the content.",
        explain: "Project-native tools stay authoritative while shared invariants—correctness, scope, synchronization, variance, provenance, and claim language—shape adversarial scenarios.",
        emphasize: "Target-dependent gaps stay visible until qualified lanes and authentic regressions exist.",
      },
      {
        purpose: "Clarify ownership of performance guidance and evidence.",
        explain: "Shared reviewers own the common evidence contract; project benchmark owners supply commands and interpretation limits; lane owners qualify environments; UXL maintains matched trials and artifacts.",
        emphasize: "Hardware qualification proves the lane, not the value of the skill or the validity of a performance claim.",
      },
      {
        purpose: "Conclude with a focused review request.",
        explain: "Ask reviewers to confirm the evidence order, correct a benchmark assumption, judge the six tasks, and identify a shared owner.",
        emphasize: "The goal is reproducible, narrowly scoped evidence before an agent makes any performance claim.",
      },
    ],
  },
];

const overviewPresenterNotes = [
  {
    purpose: "Frame the UXL Skills Evaluator for project maintainers and working-group leads.",
    explain: "It is an incubating, open project that pairs maintainable agent guidance with reproducible evaluations and a public health dashboard.",
    emphasize: "The deck explains what exists now and how maintainers can shape it; it is not a claim that the current drafts are project-approved.",
  },
  {
    purpose: "Give a factual snapshot of the current catalog and evaluation inventory.",
    explain: "There are eight skills, 52 defined tasks, 41 implemented tasks, a public dashboard, Harbor-based execution, and a portable target-lane contract.",
    emphasize: "These numbers describe inventory and maturity, not an aggregate pass rate or quality score.",
  },
  {
    purpose: "Orient the audience to the catalog structure.",
    explain: "Six skills are specific to oneAPI library projects and two cover shared SYCL troubleshooting and performance-validation practices.",
    emphasize: "Each catalog card links to the skill, its sources, its task inventory, current evidence, and a maintainer briefing.",
  },
  {
    purpose: "Explain the software architecture from source material to public evidence.",
    explain: "Maintainer-owned docs inform a versioned skill; Harbor runs task cells through hosted or qualified target lanes; artifacts feed the static dashboard.",
    emphasize: "A specialized machine changes the execution adapter and environment evidence, not the task or verification contract.",
  },
  {
    purpose: "Show what a manager can learn from the dashboard's top-level view.",
    explain: "The overview highlights maturity, coverage, freshness, ownership, platform evidence, and visible gaps across the catalog.",
    emphasize: "Health is intentionally multidimensional; the dashboard avoids compressing unlike environments into one universal score.",
  },
  {
    purpose: "Demonstrate how maintainers drill from a skill card into evaluation details.",
    explain: "The skill and evaluation views expose triggers, guidance, tasks, verifiers, treatments, results, artifacts, and known limitations.",
    emphasize: "The dashboard is a navigation and evidence layer over repository data, so every claim remains reviewable in GitHub.",
  },
  {
    purpose: "State the guiding evaluation philosophy.",
    explain: "Verify correctness and task completion first, test claims separately, preserve provenance, and keep smoke coverage distinct from discriminating evidence.",
    emphasize: "Passing an environment qualification or a task does not by itself prove that a skill improved an agent's behavior.",
  },
  {
    purpose: "Explain how comparisons remain meaningful across changing models and tools.",
    explain: "A matched evaluation cell fixes the task, model, harness, toolchain, software, environment, and verifier; only the skill treatment changes.",
    emphasize: "Results from incompatible cells are reported side by side rather than pooled into a universal benchmark number.",
  },
  {
    purpose: "Address expected questions about model, harness, and version coverage.",
    explain: "The project uses representative risk-based cells, publishes untested gaps, re-runs affected cells after material changes, and uses hidden checks and negative controls to limit overfitting.",
    emphasize: "When every treatment passes, the task remains smoke coverage and supports no claim of skill lift.",
  },
  {
    purpose: "Describe the hardware-neutral execution model.",
    explain: "GitHub-hosted runners handle portable work; qualified machines add GPUs, multi-node systems, or other specialized targets through the same task and artifact contract.",
    emphasize: "No hardware vendor receives priority from the dashboard, and qualification is separate from matched skill evaluation.",
  },
  {
    purpose: "Make the ongoing maintainer workflow concrete.",
    explain: "A typical change updates guidance or sources, adds or revises a task, runs validation, reviews evidence, and lands through a normal pull request.",
    emphasize: "The intended maintenance burden is small and periodic, with automation handling catalog checks and dashboard publication.",
  },
  {
    purpose: "Clarify which responsibilities stay with projects and which stay with UXL infrastructure.",
    explain: "Project maintainers own technical truth, triggers, limitations, and authentic cases; UXL owns schemas, validators, Harbor integration, comparison discipline, and presentation of evidence.",
    emphasize: "Named project ownership is required before an incubating skill can be treated as maintained guidance.",
  },
  {
    purpose: "Close with the smallest useful maintainer commitment.",
    explain: "Ask each project to correct its draft skill, validate or replace its task inventory, and identify a reviewer or owner for future changes.",
    emphasize: "A concrete correction or realistic issue is more valuable at this stage than broad approval of the whole system.",
  },
];

const targetPresenterNotes = [
  {
    purpose: "Introduce the target-onboarding guide for engineers adding specialized execution capacity.",
    explain: "The guide applies to GPUs, accelerators, multi-node systems, and other machines that hosted runners cannot represent faithfully.",
    emphasize: "It is intentionally vendor-neutral; the target adapter changes while the public task, verifier, and evidence contract remain stable.",
  },
  {
    purpose: "Name the five pieces that make a target lane trustworthy.",
    explain: "A public task, target adapter, machine registration, hardware oracle, and reviewable evidence bundle work together as one contract.",
    emphasize: "A reachable runner alone is not a qualified lane.",
  },
  {
    purpose: "Explain the capability contract that the machine owner must publish.",
    explain: "Labels identify the target; provenance records software and hardware; an allowlist scopes tasks; limitations state what the lane cannot establish.",
    emphasize: "Use observable capabilities and constraints rather than vendor marketing names as the contract.",
  },
  {
    purpose: "Separate the public integration surface from machine-specific configuration.",
    explain: "Tasks, schemas, qualification records, and reviewed adapter behavior live in the public repository; credentials and dispatch controls remain private.",
    emphasize: "Keeping the public surface small makes a new target easier to review and reproduce.",
  },
  {
    purpose: "Describe the hardware oracle and why it gates evaluation.",
    explain: "The oracle verifies the requested source revision, records the host, maps the intended device, runs a minimal workload, and proves the result is correct.",
    emphasize: "No model trial should run until the oracle shows that the requested target—not a fallback device—actually executed.",
  },
  {
    purpose: "Explain why dispatch and secrets belong in a private control plane.",
    explain: "The public repository defines what to run and what evidence to return; the private control repository stores machine enrollment, credentials, and restricted workflow details.",
    emphasize: "Private control protects the machine without making task definitions or accepted evidence opaque.",
  },
  {
    purpose: "Walk through safe machine preparation and runner registration.",
    explain: "Create a least-privilege account, pin required software, isolate the workspace, register ephemerally with narrow labels, and make reboot recovery unambiguous.",
    emphasize: "The machine owner must be able to stop the service and revoke access independently of the public repository.",
  },
  {
    purpose: "Explain the reviewed workflow that reaches the target.",
    explain: "A workflow dispatch selects an immutable commit and declared adapter; the runner verifies both before the oracle and Harbor execution begin.",
    emphasize: "Do not allow arbitrary repository code or unreviewed commands to execute merely because a job can reach the runner.",
  },
  {
    purpose: "Describe the operator's end-to-end run sequence.",
    explain: "Start or resume the runner, dispatch the approved workflow, watch the oracle gate, preserve the complete artifact ZIP, then clean the ephemeral workspace.",
    emphasize: "Preserve evidence before troubleshooting or cleanup so a failed run remains diagnosable.",
  },
  {
    purpose: "Explain how private artifacts become public evidence safely.",
    explain: "The importer verifies hashes, stages a sanitized qualification record, and keeps trajectories or logs with sensitive machine details access-controlled.",
    emphasize: "Publication is a reviewed step; a raw runner artifact should never appear on the public dashboard automatically.",
  },
  {
    purpose: "Place model trials after environment qualification.",
    explain: "Use tasks with measured headroom, hold the entire evaluation cell fixed, and compare skill and control treatments only after the lane is stable.",
    emphasize: "The oracle establishes execution integrity; it does not prove the skill helps or justify pooling results across environments.",
  },
  {
    purpose: "Define done for a new specialized target lane.",
    explain: "The lane is reproducible, least-privilege, oracle-gated, reviewable, documented, owned, and able to produce schema-valid sanitized evidence.",
    emphasize: "A named owner and explicit limitations are required; the project should not treat a private machine as an unexamined black box.",
  },
];

const overviewSources = [
  "https://github.com/uxlfoundation/skills",
  "https://uxlfoundation.github.io/skills/",
  "https://github.com/uxlfoundation/skills/blob/main/skills.yaml",
  "https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATOR_POLICY.md",
];

const targetSources = [
  "https://github.com/uxlfoundation/skills/blob/main/docs/target-device-adapter.md",
  "https://github.com/uxlfoundation/skills/blob/main/docs/private-machine-runner.md",
  "https://github.com/uxlfoundation/skills/tree/main/evaluation/runner",
  "https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATOR_POLICY.md",
];

function skillSources(skill) {
  return [
    `https://github.com/uxlfoundation/skills/tree/main/skills/${skill}`,
    `https://github.com/uxlfoundation/skills/blob/main/skill-cards/${skill}.md`,
    `https://github.com/uxlfoundation/skills/blob/main/docs/maintainer-review/${skill}.md`,
    "https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/suites.json",
    "https://github.com/uxlfoundation/skills/blob/main/evaluation/harbor/EVALUATOR_POLICY.md",
  ];
}

function applyPresenterNotes(presentation, notes, sources) {
  if (presentation.slides.items.length !== notes.length) {
    throw new Error(`Speaker-note count ${notes.length} does not match slide count ${presentation.slides.items.length}.`);
  }
  for (const [index, note] of notes.entries()) {
    const speakerNotes = presentation.slides.items[index].speakerNotes;
    speakerNotes.textFrame.setText([
      "[Sources]",
      ...sources.map((source) => `- ${source}`),
      "[/Sources]",
      "",
      "Presenter guidance",
      `Purpose: ${note.purpose}`,
      `Explain: ${note.explain}`,
      `Emphasize: ${note.emphasize}`,
    ].join("\n"));
    speakerNotes.setVisible(true);
  }
}

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
  const config = projectPresenterConfigs[projectName];
  const displayName = config.displayName;
  replaceText(presentation, ids.project.titles[0], `${displayName} Skills`, `${displayName} Skill`);
  const subtitle = presentation.resolve(ids.project.bodies[0]);
  subtitle.text.replace("Maintainer briefing ·", "September 2026 ·");
  presentation.slides.remove(1);
  renumberSlideFooters(presentation);
  applyPresenterNotes(presentation, projectPresenterNotes(config), skillSources(`uxl-${projectName}`));
  return finalizeDeck(presentation, templatePath, slug, 6, projectDeckSourceSlides);
}

async function buildCrossProjectDeck(deck) {
  const templatePath = path.join(sourceDir, "uxl-onednn-maintainer-briefing-template.pptx");
  const presentation = await importDeck(templatePath);
  for (let index = 0; index < deck.slides.length; index += 1) {
    const sourceIndex = projectDeckSourceIndexes[index];
    setShapeText(presentation, ids.project.titles[sourceIndex], deck.slides[index][0]);
    setShapeText(presentation, ids.project.bodies[sourceIndex], deck.slides[index][1]);
  }
  presentation.slides.remove(1);
  renumberSlideFooters(presentation);
  applyPresenterNotes(presentation, deck.notes, skillSources(deck.skill));
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
  presentation.slides.remove(1);
  renumberSlideFooters(presentation);
  applyPresenterNotes(presentation, overviewPresenterNotes, overviewSources);
  return finalizeDeck(presentation, templatePath, "uxl-skills-maintainer-overview", 13, overviewDeckSourceSlides);
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
  applyPresenterNotes(presentation, targetPresenterNotes, targetSources);
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
