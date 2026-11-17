import type { Metadata } from "next";
import { Bricolage_Grotesque, Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import { ArrowUpRightIcon } from "@phosphor-icons/react/ssr";
import { Analytics } from "@vercel/analytics/next";
import { REPO_URL } from "@/lib/catalog";
import { loadCatalog } from "@/lib/load";
import { InstallModeProvider } from "@/components/InstallMode";
import { ThemeToggle } from "@/components/ThemeToggle";
import { themeInitScript } from "@/lib/theme";
import "./globals.css";

// The ARCworks faces: Bricolage Grotesque for the wordmark and headings, Inter for text, JetBrains Mono for labels.
const display = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-display", axes: ["opsz"] });
const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: { default: "Pattern Shop", template: "%s | Pattern Shop" },
  description:
    "Pattern Shop, from WWT Digital ARCworks: skills everyone can reuse. Browse and install WWT Digital's shared Claude skills and MCP servers, grouped by category.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const repo = loadCatalog()?.marketplace.repo || REPO_URL;
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} ${mono.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body data-aw-member="pattern-shop">
        <header className="site-header">
          <div className="wrap nav">
            <Link className="brand" href="/" aria-label="Pattern Shop, home">
              <img className="brand-mark" src="/brand/pattern-shop-avatar.svg" width={30} height={30} alt="" />
              <span className="brand-word">pattern shop</span>
            </Link>
            <span className="sp" />
            <nav className="nav-links" aria-label="Primary">
              <Link className="hide-sm" href="/#install">Install</Link>
              <Link href="/#browse">Browse</Link>
              <Link href="/contribute">Contribute</Link>
              <a className="hide-sm" href={repo} target="_blank" rel="noopener">
                GitHub <ArrowUpRightIcon size={13} weight="bold" aria-hidden="true" />
              </a>
            </nav>
            <ThemeToggle />
          </div>
        </header>
        <InstallModeProvider>{children}</InstallModeProvider>
        <Analytics />
      </body>
    </html>
  );
}
