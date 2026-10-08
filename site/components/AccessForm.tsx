"use client";

import { useEffect, useState } from "react";

// The sign-in form on /access. A plain HTML POST so it works with JavaScript off; the script only
// fills in where to go afterwards and shows the error. The proxy *rewrites* gated URLs to this page,
// so the address bar still holds the page the visitor wanted: that's the default `next`.
export function AccessForm() {
  const [next, setNext] = useState("");
  const [error, setError] = useState(false);
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setError(params.get("error") === "1");
    const wanted = params.get("next");
    if (wanted) setNext(wanted);
    else if (location.pathname !== "/access") setNext(location.pathname + location.search);
  }, []);

  return (
    <form className="access-form" method="post" action="/api/access">
      <input type="hidden" name="next" value={next} />
      <label>
        <span className="visually-hidden">Access key</span>
        <input type="password" name="key" placeholder="Access key" autoComplete="off" autoFocus required />
      </label>
      <button type="submit" className="btn btn-primary">
        Continue
      </button>
      {error && (
        <p className="access-error" role="alert">
          That key didn&apos;t work. Check the pinned message in the team channel; the key changes now and then.
        </p>
      )}
    </form>
  );
}
