#!/usr/bin/env bash
# The whole loop with curl and jq: reserve an address, wait for you to send a
# message to it, poll the status, print the scores and the findings.
#
#   ./curl.sh            # English fix plan
#   ./curl.sh de         # fix plan and findings in German
#
# No key, no account. The address accepts exactly one message and expires in
# an hour; the report link is permanent.
set -euo pipefail

API="https://email-spam-tester.com/api/v1"
LANG_CODE="${1:-en}"

reservation="$(curl -sS -X POST "$API/inbox?lang=$LANG_CODE" -H 'Accept: application/json')"
address="$(jq -r .address <<<"$reservation")"
slug="$(jq -r .slug <<<"$reservation")"

echo "Send one message to: $address"
echo "Report will be at:   https://email-spam-tester.com/t/$slug"
echo "Waiting for it to arrive..."

# /status answers 202 while nothing has arrived, 200 with progress afterwards.
# The checks are final at analysis_status=checks_ready; the AI plan follows.
while :; do
  code="$(curl -sS -o /tmp/status.json -w '%{http_code}' "$API/tests/$slug/status")"
  case "$code" in
    202) sleep 5 ;;
    200)
      state="$(jq -r .analysis_status /tmp/status.json)"
      done_n="$(jq -r .checks_done /tmp/status.json)"
      total="$(jq -r .checks_total /tmp/status.json)"
      echo "  $state ($done_n/$total checks)"
      [[ "$state" == "checks_ready" || "$state" == "failed" ]] && break
      sleep 3 ;;
    410) echo "The address expired before a message arrived." >&2; exit 1 ;;
    *)   echo "Unexpected answer $code:" >&2; cat /tmp/status.json >&2; exit 1 ;;
  esac
done

report="$(curl -sS "$API/tests/$slug?lang=$LANG_CODE")"
echo
jq -r '"Score (0 to 100): \(.score_ours)  |  classic (0 to 10): \(.score_compat)  |  complete: \(.complete)"' <<<"$report"
echo
echo "Warnings and failures:"
jq -r '.checks[] | select(.status == "warn" or .status == "fail")
       | "  [\(.status)] \(.title): \(.summary)"' <<<"$report"
echo
jq -r '"Full report: \(.report_url)"' <<<"$report"
