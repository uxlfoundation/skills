import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

test("exports the UXL Skills Evaluator scorecard for GitHub Pages", async () => {
  const html = await readFile(new URL("../dist/client/index.html", import.meta.url), "utf8");
  assert.match(html, /<title>UXL Skills Evaluator<\/title>/i);
  assert.match(html, /UXL Skills Evaluator home/);
  assert.match(html, /uxl-foundation-icon-color\.svg/);
  assert.match(html, /Windows\/WSL Intel GPU lane qualified/);
  assert.match(html, /51<\/strong><span>evaluation tasks/);
  assert.match(html, /884bc80/);
  assert.match(html, /Harbor reward<\/dt><dd>1\.000/);
  assert.match(html, /https:\/\/uxlfoundation\.github\.io\/skills\/og\.png/);
  const assetMatch = html.match(/(?:src|href)="((?:\/skills)?\/_next\/[^"]+)"/);
  assert.ok(assetMatch, "expected the export to reference a compiled asset");
  const artifactPath = assetMatch[1].replace(/^\/skills/, "");
  await access(new URL(`../dist/client${artifactPath}`, import.meta.url));
  assert.doesNotMatch(html, /codex-preview|starter loading skeleton/i);
});

test("keeps source, publishing, and evidence contracts reviewable", async () => {
  const [page, layout, packageJson, nextConfig, readme] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../next.config.ts", import.meta.url), "utf8"),
    readFile(new URL("../README.md", import.meta.url), "utf8"),
  ]);

  assert.match(packageJson, /"name": "uxl-evaluator-dashboard"/);
  assert.doesNotMatch(packageJson, /openai\/sites|cloudflare|wrangler/i);
  assert.match(nextConfig, /output: "export"/);
  assert.match(nextConfig, /assetPrefix: publishingToGitHubPages \? "\/skills"/);
  assert.match(layout, /https:\/\/uxlfoundation\.github\.io\/skills/);
  assert.match(page, /https:\/\/github\.com\/uxlfoundation\/skills\/pull\/6/);
  assert.match(page, /oneDNN/);
  assert.match(page, /oneCCL/);
  assert.match(page, /SYCL build \+ debug/);
  assert.match(readme, /Raw Harbor job records.*remain in the private/s);
  assert.match(readme, /GitHub Pages/);
  await access(new URL("../public/og.png", import.meta.url));
  await access(new URL("../public/uxl-foundation-icon-color.svg", import.meta.url));
});
