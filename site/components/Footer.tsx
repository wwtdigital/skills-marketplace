import { formatDate, REPO_URL, type Catalog } from "@/lib/catalog";

export function Footer({ catalog }: { catalog: Catalog | null }) {
  const m = catalog?.marketplace;
  const repo = m?.repo || REPO_URL;
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
        <a href={`${repo}/blob/main/CONTRIBUTING.md`}>How to contribute a skill</a>
      </span>
    </footer>
  );
}
