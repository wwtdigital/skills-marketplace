import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { Prose } from "@/components/Prose";
import { loadCatalog, loadRepoDoc } from "@/lib/load";

export const metadata: Metadata = {
  title: "Contribute",
  description: "How to add a skill to the WWT Digital skills marketplace, with or without a GitHub account.",
};

// Rendered from the repo's CONTRIBUTING.md at build time, so people without access to the
// private repo can read it. Edit the markdown, not this page.
export default function ContributePage() {
  const doc = loadRepoDoc("CONTRIBUTING.md");
  return (
    <>
      <main className="wrap detail">
        {doc ? <Prose>{doc}</Prose> : <div className="empty">CONTRIBUTING.md not found.</div>}
      </main>
      <Footer catalog={loadCatalog()} />
    </>
  );
}
