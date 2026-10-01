import type { Metadata } from "next";
import { RepoDoc } from "@/components/RepoDoc";

export const metadata: Metadata = {
  title: "Changelog",
  description: "What changed in the WWTDigital skills marketplace itself: the site, how people install, and the checks behind it.",
};

// Rendered from the repo's CHANGELOG.md at build time. Edit the markdown, not this page.
export default function ChangelogPage() {
  return <RepoDoc file="CHANGELOG.md" />;
}
