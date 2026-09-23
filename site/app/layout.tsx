import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { ArrowUpRightIcon } from "@phosphor-icons/react/ssr";
import { REPO_URL } from "@/lib/catalog";
import { loadCatalog } from "@/lib/load";
import "./globals.css";

const sans = Geist({ subsets: ["latin"], variable: "--font-sans" });
const mono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: { default: "WWT Digital Skills", template: "%s | WWT Digital Skills" },
  description: "Browse and install WWT Digital's shared Claude skills and MCP servers, grouped by category.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const repo = loadCatalog()?.marketplace.repo || REPO_URL;
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body>
        <header className="site-header">
          <div className="wrap nav">
            <Link className="brand" href="/">
              <span className="brand-mark" aria-hidden="true" />
              WWT Digital Skills
            </Link>
            <span className="sp" />
            <nav className="nav-links" aria-label="Primary">
              <Link href="/#install">Install</Link>
              <Link href="/#browse">Browse</Link>
              <Link href="/contribute">Contribute</Link>
              <a className="hide-sm" href={repo} target="_blank" rel="noopener">
                GitHub <ArrowUpRightIcon size={13} weight="bold" aria-hidden="true" />
              </a>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
