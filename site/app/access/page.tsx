import type { Metadata } from "next";
import { AccessForm } from "@/components/AccessForm";

export const metadata: Metadata = {
  title: "Team access",
  robots: { index: false, follow: false },
};

// What every unauthenticated browser request is rewritten to (see ../../proxy.ts). Prerendered, so
// it reads no request data itself; the client-side form picks up `?next=` and `?error=`.
export default function AccessPage() {
  return (
    <main className="wrap doc">
      <header className="doc-head">
        <h1>This site is for the WWTDigital team</h1>
        <p className="desc">
          Paste the team access key. It&apos;s in the pinned message in the team Slack channel, along with a link that
          signs you in without typing it. It stays in this browser for 90 days.
        </p>
      </header>
      <AccessForm />
    </main>
  );
}
