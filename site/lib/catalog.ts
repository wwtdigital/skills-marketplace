// Types and pure helpers only — safe to import from client components. File access lives in load.ts.

// Shape emitted by scripts/build-index.ts, which imports these types.
export type Skill = {
  name: string;
  description: string;
  summary: string;
  body: string;
  owner: string;
  status: "draft" | "beta" | "stable";
  version: string;
  connectors: string[];
  has_scripts: boolean;
  has_references: boolean;
  updated: string;
  source: string;
  download: string;
  download_bytes: number;
  content_hash: string;
};

export type McpServer = {
  name: string;
  type: "http" | "sse" | "stdio";
  /** Remote servers only. */
  url?: string;
};

export type Plugin = {
  name: string;
  displayName: string;
  description: string;
  category: string;
  tags: string[];
  version: string;
  author: string;
  install: string;
  source: string;
  download: string;
  download_bytes: number;
  content_hash: string;
  /** MCP servers from the plugin's .mcp.json; they connect when the plugin is installed. */
  mcp_servers: McpServer[];
  skills: Skill[];
};

export type Catalog = {
  marketplace: {
    name: string;
    description: string;
    version: string;
    repo: string;
    /** Base URL this build was generated for; <site>/marketplace.json is the no-GitHub install. */
    site: string;
    install: string;
    generated: string;
    commit: string;
  };
  plugins: Plugin[];
};

export const REPO_URL = "https://github.com/wwtdigital/skills-marketplace";

/** index.json paths are relative to the site root; make them absolute so they work from any route. */
export const asset = (p: string) => "/" + p.replace(/^\/+/, "");

// Fixed locale + UTC so the static HTML doesn't depend on the build machine.
export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
