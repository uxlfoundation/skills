import { createHash } from "node:crypto";
import { execFile as execFileCallback } from "node:child_process";
import { readFile, readdir } from "node:fs/promises";
import { relative, resolve } from "node:path";
import { promisify } from "node:util";

const execFile = promisify(execFileCallback);

async function gitDirectoryDigest(directory) {
  let root;
  try {
    ({ stdout: root } = await execFile("git", ["rev-parse", "--show-toplevel"], { cwd: directory, encoding: "utf8" }));
  } catch {
    return null;
  }
  root = resolve(root.trim());
  const prefix = relative(root, directory).replaceAll("\\", "/");
  if (prefix.startsWith("../") || prefix === "..") return null;
  const { stdout } = await execFile(
    "git",
    ["ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", prefix],
    { cwd: root, encoding: "utf8", maxBuffer: 16 * 1024 * 1024 },
  );
  const repoPaths = stdout.split("\0").filter(Boolean).sort();
  const lines = [];
  for (const repoPath of repoPaths) {
    const path = resolve(root, repoPath);
    try {
      await readFile(path);
    } catch (error) {
      if (error?.code === "ENOENT" || error?.code === "EISDIR") continue;
      throw error;
    }
    const { stdout: blob } = await execFile(
      "git",
      ["hash-object", `--path=${repoPath}`, "--", path],
      { cwd: root, encoding: "utf8" },
    );
    const name = relative(directory, path).replaceAll("\\", "/");
    lines.push(`${name} ${blob.trim()}`);
  }
  return createHash("sha256").update(lines.join("\n"), "utf8").digest("hex");
}

export async function directoryDigest(directory) {
  const gitDigest = await gitDirectoryDigest(directory);
  if (gitDigest !== null) return gitDigest;
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
