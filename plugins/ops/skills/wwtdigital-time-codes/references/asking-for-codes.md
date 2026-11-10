# Asking for a code

When a code is unknown, or sources conflict in a way that changes which code to use, ask the person who owns the answer. #d-time-entry (`C0321TBF0P5`) is where people ask, and it should answer itself: the ops team isn't on call for it.

**Never tag** the ops group, the time-entry admins, `@here` or `@channel`. If an admin answers on their own, that's a bonus.

## Who to ask

**A client or pursuit code: the channel's lead.** Project and pursuit leads own their codes and post them in channel topics. Find the lead in this order:

1. A person named in the channel's topic or purpose as lead, PM or owner, or @mentioned there.
2. Whoever last set the topic. Read the channel history with `slack_read_channel` and look for the "set the channel topic" message.
3. Ask the person who leads that work.

Post the question **in that client channel**, mentioning the lead, and ask them to add the code to the topic so the whole team gets it. If there's no lead to be found, or the person would rather not post there, use #d-time-entry instead.

**An internal (non-client) code, or a rules question: #d-time-entry, with no tags.** Anyone who knows can answer.

## 1. Check for an existing question

Look in `open_questions` first. Then search #d-time-entry for the client or topic over the last 30 days, using `slack_search_public_and_private` with `keywords: ["<client>"]` and `filters: "in:<#C0321TBF0P5> after:<30 days ago>"`. For a client code, search the client channel too.

- **Already asked and answered:** use that answer.
- **Asked but not answered:** point the person to that thread. Don't ask again.

## 2. Draft one short message

The message goes out under the person's name, so write it the way they would: plain, specific, no preamble.

Include:
- the work (client, pursuit or activity) and roughly when it happened
- what you found and where, with codes in backticks and any conflict in one line
- the specific ask: which code and task to use

To a lead, in their channel:

> <@LEAD> Quick one: what's the code for Acme pursuit work this week? The topic only has the delivery project code. Could you add the Sales P&L to the topic too? Thanks!

In #d-time-entry, untagged:

> Code check: where does prep for an internal enablement session go, if the audience is sales? The Time Entry page has practice dev, and a thread from this spring said a Sales P&L.

When a timesheet week turns up several unknowns, send one message per lead, and put all the internal ones in a single #d-time-entry message as a short list.

## 3. Get a yes before posting

Posting speaks for the person, so show them the draft and wait for approval. Two exceptions:

- **Approved for the session:** if they've said to go ahead without checking for the rest of this session, you can post without asking each time.
- **Sending it themselves:** if they'd rather send it, save it with `slack_send_message_draft` instead of posting.

## 4. Post

Post with `slack_send_message` as a new top-level message: in the client channel for a lead, or to `C0321TBF0P5` for #d-time-entry. Only reply in an existing thread if it's the same question.

## 5. Record it

1. Add an entry to `open_questions` with the date, topic, question, message permalink and `status: "open"`.
2. Rebuild and republish the page, following `refresh.md` step 8.
3. Tell the person what to enter in the meantime:
   - If there's a reasonable interim choice, give it and label it interim.
   - If there isn't, suggest leaving that entry until someone answers.

## 6. Follow up

On the next lookup or refresh, read the thread of each open question with `slack_read_thread`.

- **The lead or an admin answered:** use the answer.
- **A teammate answered:** use it once the person confirms the code worked in MyTime.
- Then mark the question `answered`. Add a client code to `rows` under the matching channel with `found_in: "answer"`. Turn a general rule into a `notice`. Tell the person what came back.
- **No answer after three working days:** tell the person, and offer to ask once more in #d-time-entry, untagged. Don't escalate to ops.
