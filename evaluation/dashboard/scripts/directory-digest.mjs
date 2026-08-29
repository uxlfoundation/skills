import { createHash } from "node:crypto";
import { readFile, readdir } from "node:fs/promises";
import { relative, resolve } from "node:path";

export async function directoryDigest(directory) {
  const entries = [];
  async function visit(current) {
    const children = await readdir(current, { withFileTypes: true });
    for (const child of children) {
      const path = resolve(current, child.name);
      if (child.isDirectory()) await visit(path);
      else if (child.isFile()) entries.push(path);
    }
  }
  try {
    await visit(directory);
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
  const lines = await Promise.all(
    entries
      .sort((left, right) => {
        const leftName = relative(directory, left).replaceAll("\\", "/");
        const rightName = relative(directory, right).replaceAll("\\", "/");
        return leftName < rightName ? -1 : leftName > rightName ? 1 : 0;
      })
      .map(async (path) => {
        const name = relative(directory, path).replaceAll("\\", "/");
        const digest = createHash("sha256").update(await readFile(path)).digest("hex");
        return `${name} ${digest}`;
      }),
  );
  return createHash("sha256").update(lines.join("\n"), "utf8").digest("hex");
}
