#!/usr/bin/env node
// The whole loop with fetch (Node 18 or newer): reserve an address, wait for
// a message to arrive at it, poll the status, print the scores and the
// findings.
//
//   node node.mjs          # English fix plan
//   node node.mjs de       # fix plan and findings in German
//
// No key, no account. The address accepts exactly one message and expires in
// an hour; the report link is permanent.

const API = "https://email-spam-tester.com/api/v1";
const lang = process.argv[2] ?? "en";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function call(method, path) {
  const resp = await fetch(API + path, { method, headers: { Accept: "application/json" } });
  // 202 (nothing arrived yet), 404, 410 and 429 all carry a JSON body.
  return [resp.status, await resp.json()];
}

const [reserved, reservation] = await call("POST", `/inbox?lang=${lang}`);
if (reserved !== 200) {
  console.error("could not reserve an address:", reservation);
  process.exit(1);
}
const { slug } = reservation;
console.log("Send one message to:", reservation.address);
console.log("Report will be at:  ", `https://email-spam-tester.com/t/${slug}`);
console.log("Waiting for it to arrive...");

// /status answers 202 while nothing has arrived, 200 with progress after.
// The checks are final at analysis_status "checks_ready"; the AI plan
// (ai_status) only ever adds to the report, so it is not awaited here.
for (;;) {
  const [status, body] = await call("GET", `/tests/${slug}/status`);
  if (status === 202) { await sleep(5000); continue; }
  if (status === 410) { console.error("The address expired before a message arrived."); process.exit(1); }
  if (status !== 200) { console.error("unexpected answer", status, body); process.exit(1); }
  console.log(`  ${body.analysis_status} (${body.checks_done}/${body.checks_total} checks)`);
  if (body.analysis_status === "checks_ready" || body.analysis_status === "failed") break;
  await sleep(3000);
}

const [got, report] = await call("GET", `/tests/${slug}?lang=${lang}`);
if (got !== 200) { console.error("could not read the report:", report); process.exit(1); }

console.log();
console.log(`Score (0 to 100): ${report.score_ours}  |  classic (0 to 10): ${report.score_compat}  |  complete: ${report.complete}`);
console.log();
console.log("Warnings and failures:");
for (const check of report.checks) {
  if (check.status === "warn" || check.status === "fail") {
    console.log(`  [${check.status}] ${check.title}: ${check.summary}`);
    for (const source of check.citations?.standards ?? []) console.log(`      ${source.title}: ${source.url}`);
  }
}
console.log();
console.log("Full report:", report.report_url);
