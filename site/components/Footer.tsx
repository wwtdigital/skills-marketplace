import Link from "next/link";
import { formatDate, type Catalog } from "@/lib/catalog";

export function Footer({ catalog }: { catalog: Catalog | null }) {
  const m = catalog?.marketplace;
  return (
    <footer className="wrap">
      {m && (
        <span>
          Catalog v{m.version}
          {m.commit && ` · ${m.commit}`} · built {formatDate(m.generated)}
        </span>
      )}
      <span>
        Maintained by WWT Digital · <a href="mailto:scott.cullum@wwt.com">scott.cullum@wwt.com</a>
      </span>
      <span>
        <Link href="/contribute">How to contribute a skill</Link>
      </span>
    </footer>
  );
}
