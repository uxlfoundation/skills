import { access, rename, rm, writeFile } from "node:fs/promises";

const client = new URL("../dist/client/", import.meta.url);
const generatedAssets = new URL("skills/_next/", client);
const publishedAssets = new URL("_next/", client);

await access(new URL("index.html", client));
await access(generatedAssets);
await rm(publishedAssets, { recursive: true, force: true });
await rename(generatedAssets, publishedAssets);
await rm(new URL("skills/", client), { recursive: true, force: true });
await writeFile(new URL(".nojekyll", client), "");
