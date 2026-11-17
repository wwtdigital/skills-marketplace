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
              <div className="hero-mark rise" style={step(0)}>
                <span className="tile">
                  <img
                    src="/brand/pattern-shop-on-ink.svg"
                    width={78}
                    height={78}
                    alt="Pattern Shop mark: a sea turtle seen from above, its shell a gold pattern of plates"
                  />
                </span>
                <p className="label">
                  WWT Digital ARCworks
                  <b>Pattern Shop</b>
                </p>
              </div>
              <h1 className="rise" style={step(1)}>
                Skills everyone can reuse.
              </h1>
              <p className="hero-lead rise" style={step(2)}>
                Where the practice&rsquo;s know-how is shaped, labelled and shelved.
              </p>
              <p className="hero-sub rise" style={step(2)}>
                Install a category bundle and Claude picks up the team&apos;s workflows in Claude Code and Cowork. Every
                skill says what it&rsquo;s for, what it&rsquo;s not for, and what has to be connected before it will run.
              </p>
              <div className="hero-ctas rise" style={step(3)}>
                <a className="btn btn-primary" href="#browse">
                  Browse skills <ArrowDownIcon size={15} weight="bold" aria-hidden="true" />
                </a>
                <Link className="btn" href="/contribute">
                  Contribute a skill
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
