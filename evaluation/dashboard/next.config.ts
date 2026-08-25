import type { NextConfig } from "next";

const publishingToGitHubPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: false,
  assetPrefix: publishingToGitHubPages ? "/skills" : "",
};

export default nextConfig;
