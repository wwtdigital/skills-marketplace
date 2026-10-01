import type { Metadata } from "next";
import { RepoDoc } from "@/components/RepoDoc";

export const metadata: Metadata = {
  title: "Contribute",
  description: "How to add a skill or MCP server to the WWTDigital skills marketplace, with or without a GitHub account.",
};

// Rendered from the repo's CONTRIBUTING.md at build time. Edit the markdown, not this page.
export default function ContributePage() {
  return <RepoDoc file="CONTRIBUTING.md" />;
}
