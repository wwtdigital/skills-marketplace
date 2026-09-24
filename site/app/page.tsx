import Link from "next/link";
import { ArrowDownIcon } from "@phosphor-icons/react/ssr";
import { Catalog } from "@/components/Catalog";
import { Footer } from "@/components/Footer";
import { InstallTabs } from "@/components/InstallTabs";
import { REPO_URL } from "@/lib/catalog";
import { loadCatalog } from "@/lib/load";

const step = (i: number) => ({ "--i": i }) as React.CSSProperties;

export default function Home() {
  const catalog = loadCatalog();
  const repo = catalog?.marketplace.repo || REPO_URL;

  return (
    <>
      <main>
        <div className="wrap">
          <section className="hero">
            <div>
              <h1 className="rise" style={step(0)}>
                Skills Claude already knows how to use.
              </h1>
              <p className="hero-sub rise" style={step(1)}>
                Shared across WWTDigital. Install a category bundle and Claude picks up the team&apos;s workflows in
                Claude Code and Cowork.
              </p>
              <div className="hero-ctas rise" style={step(2)}>
                <a className="btn btn-primary" href="#browse">
                  Browse <ArrowDownIcon size={15} weight="bold" aria-hidden="true" />
                </a>
                <Link className="btn" href="/contribute">
                  Contribute
                </Link>
              </div>
            </div>
            <InstallTabs
              repo={repo}
              marketplace={catalog?.marketplace.name || "wwtdigital"}
              marketplaceUrl={catalog?.marketplace.site ? `${catalog.marketplace.site}/marketplace.json` : null}
            />
          </section>
        </div>
        {catalog ? (
          <Catalog plugins={catalog.plugins} />
        ) : (
          <div className="wrap">
            <div className="empty">
              The catalog hasn&apos;t been built yet. Run <code>npm run catalog</code>.
            </div>
          </div>
        )}
      </main>
      <Footer catalog={catalog} />
    </>
  );
}
