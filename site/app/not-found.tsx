import Link from "next/link";

export default function NotFound() {
  return (
    <main className="wrap doc">
      <header className="doc-head">
        <h1>Not found</h1>
        <p className="desc">
          That page or skill isn&apos;t in the catalog. <Link href="/#browse">Browse all skills</Link>.
        </p>
      </header>
    </main>
  );
}
