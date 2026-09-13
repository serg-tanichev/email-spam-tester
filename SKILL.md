---
name: mail-vet
description: Use before sending any email a person will receive, such as a newsletter, a transactional template, a cold outreach draft or a password reset. Sends the real message to a disposable address, gets 39 technical checks back (SPF, DKIM, DMARC, TLS, blocklists, HTML structure, unsubscribe headers), and tells you what to change so it lands in the inbox instead of Promotions or spam. Also use when someone says their mail "goes to spam", "isn't arriving", or "gets flagged".
---

# Mail Vet

Send the draft. Read the diagnosis. Fix it. Send it again.

Nothing here is scored on the wording of your prompt: the message is delivered
over SMTP to a real mail server, and everything reported is what that server
saw. Free while the service is in beta, no key, no account.

## The loop

1. **Get an address.** `get_test_address(lang="en")` reserves one. Set `lang`
   to what the person you are working for reads; the fix plan comes back in
   that language and the choice cannot be changed once the message has arrived.
2. **Send the real message to it.** Not a summary of it, not a shortened
   version: the thing that would go out. Half the checks read headers your
   sending platform adds, and a paste of the body has none of them. The address
   takes exactly one message and expires in an hour.
3. **Wait.** `wait_for_report(slug)` blocks until the analysis is done and
   returns the summary. It does not need polling.
4. **Fix what it names.** Findings come with the RFC section and the Google
   documentation page they rest on, so you can check the claim rather than
   trust it.
5. **Send again.** A new address, the corrected message, and a score you can
   compare against the first one.

## Reading the report

Two numbers, and they are not two opinions of the same thing.

- **Inbox score, 0 to 100.** Our model. Weights authentication and
  infrastructure heavily, because that is what decides delivery before a filter
  reads a word of the copy.
- **Classic score, 0 to 10.** Reproduces the SpamAssassin-style number people
  already compare against. It is there so the report is comparable to what
  somebody has seen elsewhere, not because it is the better measure.

A check is `pass`, `warn`, `fail`, `skip` or `error`. `skip` is not a pass: it
means the check did not apply, with no attachments to scan or no HTML part
to weigh.
`error` means we could not find out, which is worth saying out loud rather than
scoring as if we had.

Act on `fail` first, then `warn`. Ignore nothing on the grounds that the score
is already high: one `fail` in authentication outranks thirty passes elsewhere.

## What you cannot fix from the message alone

Some findings are DNS, not content, and the person you are working for has to
change a record. Say so plainly instead of editing the draft:

- SPF, DKIM and DMARC records, and their alignment with the From domain
- reverse DNS for the sending IP, and whether it forward-confirms
- MX records, TLS on the sending host, and blocklist entries
- MTA-STS, TLS reporting, DNSSEC, BIMI

Everything else is yours to change in the draft: subject, preheader, HTML
weight, the text part, image alt text, link shorteners, unsubscribe headers.

## Without MCP

Two requests, no key:

```bash
# 1. reserve
curl -sX POST 'https://email-spam-tester.com/api/v1/inbox?lang=en&utm_source=agent'
# -> {"address":"test-<slug>@t.email-spam-tester.com","slug":"<slug>","expires_at":"..."}

# 2. send the message to that address, then read it back
curl -s "https://email-spam-tester.com/api/v1/tests/<slug>"
# 202 while nothing has arrived; 200 with the full report once it has
```

The report is JSON: `score_ours`, `score_compat`, `subscores`, `checks[]` with
`status`, `summary` and `citations`, and `fixes[]` with the expected gain of
each. `report_url` in the response is the human-readable page. Hand that to the
person rather than pasting a wall of JSON.

Full reference: https://email-spam-tester.com/api/docs
Every check explained: https://email-spam-tester.com/docs/

## Habits that make this useful

**Test the message you are actually going to send.** A rewritten sample
measures the sample.

**Re-test after fixing.** The expected gains in `fixes[]` are computed by
re-scoring, but they are computed one fix at a time and they do not compose;
the only honest number is the second report.

**Do not test somebody else's mail without asking.** The report shows the
subject line, the sender, the bounce address and the full source to anyone
holding the link.

**Send from the platform, not from your own client.** Testing a Mailchimp
campaign from a personal Gmail account measures Gmail.
