import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("https://evaluator.example/", {
      headers: { accept: "text/html", host: "evaluator.example" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the UXL evaluator scorecard", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>UXL Evaluator Control Room<\/title>/i);
  assert.match(html, /Windows\/WSL Intel GPU lane qualified/);
  assert.match(html, /51<\/strong><span>evaluation tasks/);
  assert.match(html, /f3481bb/);
  assert.match(html, /Harbor reward<\/dt><dd>1\.000/);
  assert.match(html, /https:\/\/evaluator\.example\/og\.png/);
  assert.doesNotMatch(html, /codex-preview|starter loading skeleton/i);
});

test("keeps source, hosting, and evidence contracts reviewable", async () => {
  const [page, layout, packageJson, hosting, readme] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
    readFile(new URL("../README.md", import.meta.url), "utf8"),
  ]);

  assert.match(packageJson, /"name": "uxl-evaluator-dashboard"/);
  assert.match(hosting, /"project_id": "appgprj_[a-f0-9]+"/);
  assert.match(layout, /images: \[\{ url: image, width: 1200, height: 630 \}\]/);
  assert.match(page, /https:\/\/github\.com\/uxlfoundation\/skills\/pull\/6/);
  assert.match(page, /oneDNN/);
  assert.match(page, /oneCCL/);
  assert.match(page, /SYCL build \+ debug/);
  assert.match(readme, /Raw Harbor job records.*remain in the private/s);
  await access(new URL("../public/og.png", import.meta.url));
});
