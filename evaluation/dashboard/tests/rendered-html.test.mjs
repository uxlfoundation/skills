import assert from "node:assert/strict";
import { access, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { directoryDigest } from "../scripts/directory-digest.mjs";

const dashboardRoot = new URL("../", import.meta.url);
const clientRoot = new URL("../dist/client/", import.meta.url);

async function exportedPage(path = "index.html") {
  return readFile(new URL(path, clientRoot), "utf8");
}

test("uses the canonical cross-platform directory digest", async () => {
  const root = await mkdtemp(join(tmpdir(), "uxl-dashboard-digest-"));
  try {
    await mkdir(join(root, "sub"));
    await writeFile(join(root, "a.txt"), "alpha");
    await writeFile(join(root, "sub", "b.txt"), "beta");
    assert.equal(
      await directoryDigest(root),
      "e081ef401f7f57797868df34df60540cd9f6f033d8b3b862e9440fafafd33c57",
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("exports a vendor-neutral UXL Skills Evaluator overview", async () => {
  const html = await exportedPage();
  assert.match(html, /<title>UXL Skills Evaluator<\/title>/i);
  assert.match(html, /UXL Skills Evaluator home/);
  assert.match(html, /Continuous evidence/);
  assert.match(html, /41 \/ 52/);
  assert.match(html, /9<\/strong><span>tasks with headroom/);
  assert.match(html, /0 \/ 8/);
  assert.match(html, /Hardware is a dimension/);
  assert.doesNotMatch(html, /Windows\/WSL Intel GPU lane qualified|Intel GPU oracle|Evidence you can.*real hardware/is);
  assert.match(html, /https:\/\/uxlfoundation\.github\.io\/skills\/og\.png/);
  assert.match(html, /skills\/#uxl-onednn/);
  assert.match(html, /platforms\//);
  assert.match(html, /methodology\//);

  const assetMatch = html.match(/(?:src|href)="((?:\/skills)?\/_next\/[^"]+)"/);
  assert.ok(assetMatch, "expected the export to reference a compiled asset");
  const artifactPath = assetMatch[1].replace(/^\/skills/, "");
  await access(new URL(`.${artifactPath}`, clientRoot));
  assert.doesNotMatch(html, /codex-preview|starter loading skeleton/i);
});

test("exports skill, evaluation, platform, and methodology drill-downs", async () => {
  const [skillHtml, evaluationHtml, platformHtml, methodologyHtml] = await Promise.all([
    exportedPage("skills/index.html"),
    exportedPage("evaluations/index.html"),
    exportedPage("platforms/index.html"),
    exportedPage("methodology/index.html"),
  ]);

  assert.match(skillHtml, /Eight accountable portfolios/);
  assert.match(skillHtml, /oneDNN/);
  assert.match(skillHtml, /oneCCL/);
  assert.match(skillHtml, /maintainer review needed/);
  assert.match(evaluationHtml, /Evaluation explorer/);
  assert.match(evaluationHtml, /<strong>52<\/strong> of/);
  assert.match(evaluationHtml, /structured evidence records/);
  assert.match(evaluationHtml, /Not yet recorded in the v1 contract/);
  assert.match(evaluationHtml, /Matched evidence health/);
  assert.match(evaluationHtml, /No v1 cells retained yet/);
  assert.match(evaluationHtml, /onednn-matmul-memory-descriptors/);
  assert.match(platformHtml, /Evidence contract first/);
  assert.match(platformHtml, /Vendor neutral/);
  assert.match(platformHtml, /Environment evidence by skill/);
  assert.match(platformHtml, /Project skill<\/span><span>Hosted CPU/);
  assert.match(platformHtml, /Skill comparison<\/dt><dd>Not yet run/);
  assert.match(methodologyHtml, /Correctness first/);
  assert.match(methodologyHtml, /No-skill, previous-skill, candidate-skill/i);
  assert.match(methodologyHtml, /Invalidate honestly/);
});

test("keeps generated data, source, publishing, and privacy contracts reviewable", async () => {
  const [page, layout, packageJson, nextConfig, readme, generated] = await Promise.all([
    readFile(new URL("app/page.tsx", dashboardRoot), "utf8"),
    readFile(new URL("app/layout.tsx", dashboardRoot), "utf8"),
    readFile(new URL("package.json", dashboardRoot), "utf8"),
    readFile(new URL("next.config.ts", dashboardRoot), "utf8"),
    readFile(new URL("README.md", dashboardRoot), "utf8"),
    readFile(new URL("app/dashboard-data.json", dashboardRoot), "utf8"),
  ]);

  assert.match(packageJson, /"data:generate"/);
  assert.doesNotMatch(packageJson, /openai\/sites|cloudflare|wrangler/i);
  assert.match(nextConfig, /output: "export"/);
  assert.match(nextConfig, /assetPrefix: publishingToGitHubPages \? "\/skills"/);
  assert.match(layout, /Vendor-neutral portfolio health/);
  assert.match(page, /capabilityCoverage/);
  assert.match(readme, /Raw Harbor job records.*remain in the private/s);
  assert.match(readme, /GitHub Pages/);
  const data = JSON.parse(generated);
  assert.equal(data.skills.length, 8);
  assert.equal(data.skills.flatMap((skill) => skill.tasks).length, 52);
  assert.ok(Array.isArray(data.evaluationCells));
  await access(new URL("public/og.png", dashboardRoot));
  await access(new URL("public/uxl-foundation-icon-color.svg", dashboardRoot));
});
