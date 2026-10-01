import type { Metadata } from "next";
import { RepoDoc } from "@/components/RepoDoc";

export const metadata: Metadata = {
  title: "Catalog",
  description: "What is in the WWTDigital skills library today, and release notes for every plugin and skill.",
};

// Rendered from the repo's CATALOG.md at build time. Edit the markdown, not this page.
export default function CatalogPage() {
  return <RepoDoc file="CATALOG.md" />;
}
