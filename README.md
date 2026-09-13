# Email Spam Tester

Email Spam Tester is a free, independent email deliverability testing tool built by Serhii Tanichev.

You send one real message to a disposable address. A mail server that behaves like a receiving one accepts it, and 41 checks run against what that server saw: SPF, DKIM, DMARC and ARC with alignment, reverse DNS, HELO, MX, TLS, more than twenty blocklists, two independent spam engines, the HTML and the links, and the rules Gmail and Yahoo enforce for bulk senders since 2024. Every warning quotes the RFC section it rests on, and the Google page where Google states its own rule. Then a fix plan, with the points for each fix recomputed by re-scoring the corrected message rather than estimated.

- Site: https://email-spam-tester.com/
- Every check explained: https://email-spam-tester.com/docs/
- API reference: https://email-spam-tester.com/api-docs/
- Changelog: https://email-spam-tester.com/changelog/ (mirrored in [CHANGELOG.md](CHANGELOG.md))
- Blog: https://email-spam-tester.com/blog/
- Privacy: https://email-spam-tester.com/privacy/ · Terms: https://email-spam-tester.com/terms/

Started in August 2026. Independent project. The first 100,000 reports are free for everyone: no signup, no card, no API key, no cap per person. Report links are permanent. The report reads in 31 languages.

## What this repository is

The public face of the project: how to use it from a script or an agent, the agent skill file, the MCP client configuration, and the changelog. The service itself is not open source; what is here is documentation and examples, under the MIT license in [LICENSE](LICENSE).

## About

I'm Serhii Tanichev, an independent software developer. I built Email Spam Tester because most email testing tools either hide the technical detail behind a single number or want an account before they show you anything. I wanted a report that names the check, quotes the rule the check rests on, and says what to change in the order that moves the score most. I build and maintain it on my own. More on the [about page](https://email-spam-tester.com/about/).

## Using it from the site

Open https://email-spam-tester.com/, copy the disposable address, send it the message you were about to send your list, from the platform that would send it. The report appears on the same page a couple of minutes after the message arrives. The address accepts exactly one message and expires in an hour.

## Using it from a script

The loop is three calls and one email. No key, no account.

1. `POST https://email-spam-tester.com/api/v1/inbox` reserves an address. Optional query parameter `lang` (an ISO code) sets the language of the fix plan and the findings.

   ```json
   {"address": "test-<slug>@t.email-spam-tester.com",
    "slug": "<slug>",
    "expires_at": "2026-01-01T12:00:00Z"}
   ```

   Use the `address` the API returns. The domain it is on is not part of the contract.

2. Send the message over SMTP to that address.

3. `GET https://email-spam-tester.com/api/v1/tests/<slug>/status` is the cheap thing to poll. It answers `202` with the reservation while no message has arrived, and `200` with the progress afterwards:

   ```json
   {"slug": "<slug>", "analysis_status": "checks_ready", "ai_status": "running",
    "checks_done": 41, "checks_total": 41}
   ```

   `analysis_status` runs `received`, `analyzing`, `checks_ready`, `failed`. `ai_status` runs `pending`, `running`, `ready`, `fallback`, `error`. The checks are final at `checks_ready`; the AI status only ever adds the plan.

4. `GET https://email-spam-tester.com/api/v1/tests/<slug>` is the report. `GET .../tests/<slug>/message` is the message as delivered: headers in wire order, both bodies, attachments, the raw source, for two days after arrival.

Other answers: `404` for an unknown slug, `410` once a reservation or a report has expired, `429` when a free-test limit applies (it does not while the free allowance lasts).

Working examples, each running the whole loop and printing the scores and the findings:

- [examples/curl.sh](examples/curl.sh)
- [examples/python.py](examples/python.py), standard library only
- [examples/node.mjs](examples/node.mjs), Node 18 or newer

The full field list is in the [API reference](https://email-spam-tester.com/api-docs/) and, for machines, in [llms-full.txt](https://email-spam-tester.com/llms-full.txt) and the [OpenAPI description](https://email-spam-tester.com/api/openapi.json).

## Using it from an agent

- **MCP.** `https://email-spam-tester.com/mcp`, streamable HTTP, four tools: `get_test_address`, `wait_for_report`, `get_report`, `get_message_source`. `wait_for_report` blocks until the analysis is done, so there is nothing to poll. Client configuration in [mcp/](mcp/README.md).
- **Skill.** [SKILL.md](SKILL.md) is the same instructions as a file: when to reach for the tool, how to read the report, which findings are DNS records a person has to change rather than text an agent can edit. Also served at https://email-spam-tester.com/skill/SKILL.md.

## What the report contains

- `score_ours`, 0 to 100. Authentication and infrastructure carry most of the weight, because they decide delivery before a filter reads a word.
- `score_compat`, 0 to 10, reproducing the SpamAssassin-style number so the report is comparable with what an older tool would say about the same message.
- `subscores` on the same 0 to 100 scale for `auth`, `infra_spam`, `content` and `compliance`.
- `checks[]`, all 41, each with `id`, `category`, `status`, `title`, `summary`, `evidence`, the two weights and `citations`: the RFC section with the sentence quoted verbatim, the receiver's own page where one exists.
- `complete`, false when a check could not run. An unchecked item is never a pass.
- `fixes[]`, the plan, ordered by the points each change is worth.
- `report_url`, the page for a person. Hand a person this, not the JSON.

A check status of `skip` is not a pass: the check did not apply. `error` means it could not run and is left out of the score.

## Found a bug?

Open an issue here, or email hi@email-spam-tester.com. A wrong citation, a check that fires when it should not, an RFC read too quickly: those get fixed first. Include the report link if you have one; it shows the subject and the sender of the tested message, so send it only if that is fine with you.

## License

The examples and documentation in this repository are released under the MIT license, see [LICENSE](LICENSE). The license covers this repository only, not the service.
