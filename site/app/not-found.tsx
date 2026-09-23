import Link from "next/link";

export default function NotFound() {
  return (
    <main className="wrap detail">
      <h1>Not found</h1>
      <p className="muted">
        That skill isn&apos;t in the catalog. <Link href="/#browse">Browse all skills</Link>.
      </p>
    </main>
  );
}
