# Asking the ops team

When a code is unknown, or sources conflict in a way that changes which code to use, ask the people who own the codes. Post the question in #d-time-entry (`C0321TBF0P5`) and tag the ops group `<!subteam^S0BECPY6SET>`.

## 1. Check for an existing question

Look in `open_questions` first. Then search #d-time-entry for the client or topic over the last 30 days, using `slack_search_public_and_private` with `keywords: ["<client>"]` and `filters: "in:<#C0321TBF0P5> after:<30 days ago>"`.

- **Already asked and answered:** use that answer.
- **Asked but not answered:** point the person to that thread. Don't ask again.

## 2. Draft one short message

The message goes out under the person's name, so write it the way they would: plain, specific, no preamble.

Include:
- the work (client, pursuit or activity) and roughly when it happened
- what you found and where, with codes in backticks and any conflict in one line (e.g. "the Notion page says Admin 1.15, a Feb thread says 1.23")
- the specific ask: which code and task to use

> <!subteam^S0BECPY6SET> Quick code check: for Acme pursuit work this week, is `116158` GES Tennessee still right? It's from a Sept thread and there's no Acme channel. Thanks!

When a timesheet week turns up several unknowns, put them all in one message as a short list.

## 3. Get a yes before posting

Posting in a shared channel speaks for the person, so show them the draft and wait for approval. Two exceptions:

- **Approved for the session:** if they've said to go ahead without checking for the rest of this session, you can post without asking each time.
- **Sending it themselves:** if they'd rather send it, save it with `slack_send_message_draft` instead of posting.

## 4. Post

Post with `slack_send_message` to `C0321TBF0P5` as a new top-level message, which is how that channel works. Only reply in someone else's thread if it's the same question.

## 5. Record it

1. Add an entry to `open_questions` with the date, topic, question, message permalink and `status: "open"`.
2. Rebuild and republish the page, following `refresh.md` step 8.
3. Tell the person what to enter in the meantime:
   - If there's a reasonable interim choice, give it and label it interim.
   - If there isn't, suggest leaving that entry until ops answers.

## 6. Follow up

On the next lookup or refresh, read the thread of each open question with `slack_read_thread`. When an ops person has answered:

- Mark the question `answered`.
- If the answer is a client-specific code, add it to `rows` under the matching channel, or the closest one, with `found_in: "#d-time-entry"`.
- If the answer is a general rule, turn it into a `notice`.
- Tell the person what came back.
