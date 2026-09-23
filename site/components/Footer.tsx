import Link from "next/link";
import { formatDate, REPO_URL, type Catalog } from "@/lib/catalog";

export function Footer({ catalog }: { catalog: Catalog | null }) {
  const m = catalog?.marketplace;
  return (
    <footer className="site-footer">
      <div className="wrap">
        <span>WWTDigital Skills{m && `, updated ${formatDate(m.generated)}`}</span>
        <nav aria-label="Footer">
          <Link href="/contribute">Contribute</Link>
          <a href="mailto:scott.cullum@wwt.com">Contact the maintainer</a>
          <a href={m?.repo || REPO_URL} target="_blank" rel="noopener">
            GitHub
          </a>
        </nav>
      </div>
    </footer>
  );
}
