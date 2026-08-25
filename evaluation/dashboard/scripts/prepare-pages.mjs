import { access, mkdir, rename, rm, writeFile } from "node:fs/promises";

const client = new URL("../dist/client/", import.meta.url);
const generatedAssets = new URL("skills/_next/", client);
const publishedAssets = new URL("_next/", client);

await access(new URL("index.html", client));
await access(generatedAssets);
await rm(publishedAssets, { recursive: true, force: true });
await rename(generatedAssets, publishedAssets);

for (const route of ["skills", "evaluations", "platforms", "methodology"]) {
  const routeDirectory = new URL(`${route}/`, client);
  await mkdir(routeDirectory, { recursive: true });
  await rename(new URL(`${route}.html`, client), new URL("index.html", routeDirectory));
  await rename(new URL(`${route}.rsc`, client), new URL("index.rsc", routeDirectory));
}

await writeFile(new URL(".nojekyll", client), "");
