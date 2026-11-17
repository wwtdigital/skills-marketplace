import Link from "next/link";
import { formatDate, REPO_URL, type Catalog } from "@/lib/catalog";

export function Footer({ catalog }: { catalog: Catalog | null }) {
  const m = catalog?.marketplace;
  return (
    <footer className="site-footer">
      <div className="wrap">
        <span className="sig">
          <img src="/brand/pattern-shop-avatar.svg" width={28} height={28} alt="" />
          <span>
            <b>Pattern Shop</b>
            Part of WWT Digital ARCworks{m && `. Updated ${formatDate(m.generated)}`}
          </span>
        </span>
        <nav aria-label="Footer">
          <Link href="/catalog">Catalog</Link>
          <Link href="/changelog">Changelog</Link>
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
