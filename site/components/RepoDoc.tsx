import { Footer } from "@/components/Footer";
import { headings, Prose } from "@/components/Prose";
import { loadCatalog, loadRepoDoc } from "@/lib/load";

// A markdown file from the repo root, rendered at build time with a contents list, so people without
// access to the repo can read it. Edit the markdown, not the page that uses this.
export function RepoDoc({ file }: { file: string }) {
  const doc = loadRepoDoc(file);
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
          <div className="empty">{file} not found.</div>
        )}
      </main>
      <Footer catalog={loadCatalog()} />
    </>
  );
}
