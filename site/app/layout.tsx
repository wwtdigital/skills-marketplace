import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import { REPO_URL } from "@/lib/catalog";
import { loadCatalog } from "@/lib/load";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: { default: "WWT Digital Skills", template: "%s · WWT Digital Skills" },
  description: "Browse and install WWT Digital's shared Claude skills, grouped by category.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const repo = loadCatalog()?.marketplace.repo || REPO_URL;
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>
        <header>
          <div className="wrap nav">
            <Link className="brand" href="/">
              <span className="dot" />
              WWT Digital Skills
            </Link>
            <span className="sp" />
            <Link className="lnk" href="/#install">
              Install
            </Link>
            <Link className="lnk" href="/#browse">
              Browse
            </Link>
            <a className="lnk" href={repo} target="_blank" rel="noopener">
              GitHub
            </a>
            <Link className="lnk" href="/contribute">
              Contribute
            </Link>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
