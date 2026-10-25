# Building the page without Python

`scripts/build_page.py` needs `python3`. Use it when it's there. When it isn't, do the same steps yourself, as below. The page has to carry the same data and pass the same checks; whitespace in the JSON can differ.

## Is Python available?

Check without running Python, because on some machines running it opens an installer:

- **No shell tool** (for example, a chat with no code execution): not available.
- **`command -v python3` prints nothing:** not available.
- **macOS, `command -v python3` is `/usr/bin/python3`, and `xcode-select -p` fails:** not available. That `python3` is a stub that opens a "Command Line Tools" install dialog. Don't run it, and don't ask the person to install anything just for this.
- **Windows, and `python3` opens the Microsoft Store or prints an install hint:** not available.
- **Anything else:** run the script. If it fails before printing `OK` or `ERROR:` (command not found, a dialog, a crash), treat Python as unavailable and use the steps below. An `ERROR:` line is the script working: fix the data and run it again.

Decide once per session, and don't mention Python to the person unless they ask.

## extract (page → data)

1. Find `<script type="application/json" id="bill-codes-data">` in the saved page and take everything up to the next `</script>`.
2. Parse it as JSON. (`<\/` inside it is a valid JSON escape for `</`.) If there's no such block, or it doesn't parse, stop: this isn't a My Time Codes page.

## build (data → page)

1. **Validate the data**, the same way the script does. Collect every problem before stopping:
   - Top level has `owner`, `slack_user_id`, `workspace`, `generated` and `channels_scanned`.
   - `rows`, `standing`, `notices`, `references`, `no_code_channels` and `open_questions` are lists (use `[]` for any that are missing).
   - Every row has a non-empty `channel`, `channel_id`, `code` and `code_type`, and `code_type` is `project`, `sales_pl` or `indirect`. Fill in any missing `task` with `""`, `label` with `"(unlabeled)"` and `found_in` with `"topic"`.
   - Every notice has a `flag`.
   - Every open question has `status` `open` or `answered`.

   If anything fails, fix the data and validate again. Never publish data that fails.
2. **Read `references/page-template.html`** and confirm it contains `__DATA__` exactly once.
3. **Serialize the data** as JSON, then replace every `</` with `<\/` so no value can close the script tag early.
4. **Replace `__DATA__`** with that JSON, and change nothing else in the template.
5. **Check the result:** extract the block from the new page (as above) and confirm it parses and has the same number of rows. Only then publish.

Report the same summary the script prints: rows, channels, standing codes, notices, open questions, and channels scanned.
