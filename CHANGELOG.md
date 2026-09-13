# Changelog

All notable changes to Email Spam Tester, newest first. The same list is published at https://email-spam-tester.com/changelog/.

What changed in the tool and when, newest first: checks, the report, the API, fixes. I keep this by hand from the commit history, so the dates are the days the change was made. The project started on August 14, 2026.

## 2026-09-13

- Dropped the three SORBS zones from the blocklist roster. SORBS shut down in 2024 and its zones answer "not listed" to everyone, which is not information. The infrastructure check now queries 21 lists.

## 2026-09-04

- The AI fix plan no longer times out and retries on a slow minute. The advisor has its own clock now, and a slow response costs you a wait rather than the plan.

## 2026-08-24

- DMARC report addresses are checked. The report warns when a `rua` or `ruf` address will never receive anything, and when a record lists more report addresses than a receiver owes you.
- Citations point at the DMARC RFC that is in force, and a finding that outlived its rule was dropped.
- Return paths that bulk senders actually use, the per-recipient bounce addresses, are no longer refused. The report shows them.

## 2026-08-22

- Reports are served in the language they are being read in, with translation on demand, and the report shows whole while the translation is on its way.
- A written [API reference](/api-docs/) in 31 languages replaced the generated Swagger page, with a sandbox next to it.
- Backups three times a day, kept for five days, verified every week by restoring the newest one.
- The agent page and SKILL.md in every language. The last English left on a translated report is gone: 99 interface labels translated, and every long dash taken out of them.
- An SPF record's lookup cost is now counted as what the record costs, not what this one message paid.

## 2026-08-21

- Moved to a server of its own. No daily quota, and report links are permanent.
- MCP server with four tools, so an agent can reserve an address, wait for the report and read it.
- Every warning and failure carries the section of the standard it rests on, quoted, plus the Google page where one exists. 79 sources behind 36 of the checks.
- The site and the report in 31 languages. Documentation for every check. The AI plan is written in the reader's language.
- A logo, an icon set, a language switch that keeps your test, and the report page translated.

## 2026-08-19

- The AI plan moved under the score and the wait has something to watch: a stage and a count of seconds.
- The AI verdict is a description now, not a headline. The headline is computed from the score.
- An unaligned envelope no longer counts as a DMARC failure when DKIM is aligned.
- The message as received: headers in wire order, both bodies, attachments, raw source.

## 2026-08-17

- MIME-encoded headers are decoded before their length is measured.
- Test addresses match regardless of case, so a mangled address still finds its inbox.

## 2026-08-15

- The classic score is calibrated against what mail-tester.com actually charges for the same message. The side-by-side comparison that came out of it is in the repository.
- The blocklist roster was audited against reality and three dead lists were dropped. One slow blocklist can no longer mark every report incomplete.
- A retention worker, end-to-end pipeline tests, and a link fetcher hardened against requests to internal addresses.

## 2026-08-14

- Started. Scoring model, message parser, the authentication and infrastructure evaluators, the DNS and blocklist collectors, and inbound port 25 verified end to end.
