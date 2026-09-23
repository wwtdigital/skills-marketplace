import { Catalog } from "@/components/Catalog";
import { InstallTabs } from "@/components/InstallTabs";
import { Footer } from "@/components/Footer";
import { REPO_URL } from "@/lib/catalog";
import { loadCatalog } from "@/lib/load";

export default function Home() {
  const catalog = loadCatalog();
  const repo = catalog?.marketplace.repo || REPO_URL;
  const skills = catalog?.plugins.flatMap((p) => p.skills) ?? [];

  return (
    <>
      <main className="wrap">
        <section className="hero">
          <h1>Skills Claude already knows how to use — shared across WWT Digital.</h1>
          <p>
            Install the bundles you need and Claude picks up the team&apos;s workflows in Claude Code and
            Cowork. No GitHub account? Download any skill as a file below.
          </p>
          {catalog && (
            <div className="stats">
              <span>
                <b>{catalog.plugins.length}</b> plugins
              </span>
              <span>
                <b>{skills.length}</b> skills
              </span>
              <span>
                <b>{catalog.plugins.reduce((n, p) => n + p.mcp_servers.length, 0)}</b> MCP servers
              </span>
              <span>
                <b>{skills.filter((s) => s.status === "stable").length}</b> stable
              </span>
            </div>
          )}
        </section>

        <InstallTabs
          repo={repo}
          marketplace={catalog?.marketplace.name || "wwt-digital"}
          marketplaceUrl={catalog?.marketplace.site ? `${catalog.marketplace.site}/marketplace.json` : null}
        />

        {catalog ? (
          <Catalog plugins={catalog.plugins} />
        ) : (
          <div className="empty">
            Catalog not built yet. Run <code>npm run catalog</code>.
          </div>
        )}
      </main>
      <Footer catalog={catalog} />
    </>
  );
}
