"""
One way to start a headless browser, for every script that renders.

Playwright's default is its own Chromium build, a separate 150MB download that most people
never finish. Almost every machine already has Google Chrome or Microsoft Edge, and Playwright
can drive either through a "channel". So: use the browser the person already has, and only
fall back to Playwright's Chromium when there is none.

    from browser import launch
    with sync_playwright() as p:
        b = launch(p)

WWT_BROWSER picks one explicitly: chrome, msedge, or chromium (Playwright's own build).
"""
import os

CHANNELS = ("chrome", "msedge")


def launch(p, **kw):
    want = os.environ.get("WWT_BROWSER", "").strip().lower()
    order = [want] if want else list(CHANNELS) + ["chromium"]
    errors = []
    for ch in order:
        try:
            if ch == "chromium":
                return p.chromium.launch(**kw)
            return p.chromium.launch(channel=ch, **kw)
        except Exception as e:  # not installed, or will not start: try the next one
            errors.append("%s: %s" % (ch, str(e).strip().split("\n")[0][:120]))
    raise RuntimeError(
        "no browser could be started. Install Google Chrome or Microsoft Edge, or run the "
        "plugin setup, which installs one.\n  " + "\n  ".join(errors))

