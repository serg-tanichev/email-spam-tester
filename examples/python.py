#!/usr/bin/env python3
"""The whole loop with the standard library: reserve an address, wait for a
message to arrive at it, poll the status, print the scores and the findings.

    python3 python.py          # English fix plan
    python3 python.py de       # fix plan and findings in German

No key, no account. The address accepts exactly one message and expires in an
hour; the report link is permanent.
"""
import json
import sys
import time
import urllib.error
import urllib.request

API = "https://email-spam-tester.com/api/v1"


def call(method: str, path: str) -> tuple[int, dict]:
    req = urllib.request.Request(API + path, method=method,
                                 headers={"Accept": "application/json"}, data=b"" if method == "POST" else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as err:
        # 202 (nothing arrived yet), 404, 410 and 429 all come with a JSON body.
        return err.code, json.load(err)


def main() -> int:
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"

    status, reservation = call("POST", f"/inbox?lang={lang}")
    if status != 200:
        print("could not reserve an address:", reservation, file=sys.stderr)
        return 1
    slug = reservation["slug"]
    print("Send one message to:", reservation["address"])
    print("Report will be at:  ", f"https://email-spam-tester.com/t/{slug}")
    print("Waiting for it to arrive...")

    # /status answers 202 while nothing has arrived, 200 with progress after.
    # The checks are final at analysis_status == "checks_ready"; the AI plan
    # (ai_status) only ever adds to the report, so we do not wait for it here.
    while True:
        status, body = call("GET", f"/tests/{slug}/status")
        if status == 202:
            time.sleep(5)
            continue
        if status == 410:
            print("The address expired before a message arrived.", file=sys.stderr)
            return 1
        if status != 200:
            print("unexpected answer", status, body, file=sys.stderr)
            return 1
        print(f"  {body['analysis_status']} ({body['checks_done']}/{body['checks_total']} checks)")
        if body["analysis_status"] in ("checks_ready", "failed"):
            break
        time.sleep(3)

    status, report = call("GET", f"/tests/{slug}?lang={lang}")
    if status != 200:
        print("could not read the report:", report, file=sys.stderr)
        return 1

    print()
    print(f"Score (0 to 100): {report['score_ours']}  |  classic (0 to 10): "
          f"{report['score_compat']}  |  complete: {report['complete']}")
    print()
    print("Warnings and failures:")
    for check in report["checks"]:
        if check["status"] in ("warn", "fail"):
            print(f"  [{check['status']}] {check['title']}: {check['summary']}")
            for source in check.get("citations", {}).get("standards", []):
                print(f"      {source['title']}: {source['url']}")
    print()
    print("Fix plan:")
    for fix in report.get("fixes", []):
        print(" ", json.dumps(fix, ensure_ascii=False)[:200])
    print()
    print("Full report:", report["report_url"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
