import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { headings, Prose } from "@/components/Prose";
import { loadCatalog, loadRepoDoc } from "@/lib/load";

export const metadata: Metadata = {
  title: "Contribute",
  description: "How to add a skill or MCP server to the WWT Digital skills marketplace, with or without a GitHub account.",
};

// Rendered from the repo's CONTRIBUTING.md at build time, so people without access to the
// private repo can read it. Edit the markdown, not this page.
export default function ContributePage() {
  const doc = loadRepoDoc("CONTRIBUTING.md");
  const toc = doc ? headings(doc) : [];
  return (
    <>
      <main className="wrap doc">
        {doc ? (
          <div className="doc-grid toc-left" style={{ marginTop: 0 }}>
            <nav className="toc" aria-label="On this page">
              {toc.map((h) => (
                <a key={h.id} href={`#${h.id}`}>
                  {h.text}
                </a>
              ))}
            </nav>
            <Prose>{doc}</Prose>
          </div>
        ) : (
          <div className="empty">CONTRIBUTING.md not found.</div>
        )}
      </main>
      <Footer catalog={loadCatalog()} />
    </>
  );
}
