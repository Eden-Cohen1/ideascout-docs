#!/usr/bin/env python3
"""Finalize a merged docs proposal: append the terminal `published` ledger line and post
"Published" into the proposal's Slack thread. Runs in GitHub Actions (Option A), no LLM.

Env: HEAD_REF (proposal/pr-<n>), DOCS_PR (docs-repo PR number),
     SLACK_BOT_TOKEN, DOCS_SLACK_CHANNEL.
"""
import os
import re
import json
import urllib.request
from datetime import datetime, timezone

LEDGER = "proposals/ledger.jsonl"

head_ref = os.environ.get("HEAD_REF", "")
docs_pr = int(os.environ.get("DOCS_PR", "0") or 0)
slack_token = os.environ.get("SLACK_BOT_TOKEN", "")
slack_channel = os.environ.get("DOCS_SLACK_CHANNEL", "")

m = re.search(r"\d+", head_ref)
if not m:
    print(f"no source PR number in head ref '{head_ref}'; nothing to finalize")
    raise SystemExit(0)
src_pr = int(m.group(0))


def read_ledger():
    try:
        with open(LEDGER) as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    except FileNotFoundError:
        return


thread, outcome, already = "", "update-doc", False
for o in read_ledger():
    if o.get("pr") == src_pr and o.get("event") == "proposed":
        thread = o.get("threadTs") or thread
        outcome = o.get("outcome") or outcome
    if o.get("pr") == src_pr and o.get("event") == "published":
        already = True

if already:
    print(f"PR {src_pr} already has a published entry; skipping ledger append")
else:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {
        "ts": ts, "pr": src_pr, "event": "published", "outcome": outcome,
        "proposalPr": docs_pr, "approvedBy": "github-merge", "note": "merged on GitHub",
    }
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"appended published entry for source PR {src_pr}")

# Post "Published" into the same Slack thread (best-effort; never fail the job on Slack).
if thread and slack_token and slack_channel:
    body = json.dumps({
        "channel": slack_channel,
        "thread_ts": thread,
        "text": f"Published ✅  docs PR #{docs_pr} merged to main.",
    }).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage", data=body,
        headers={"Authorization": f"Bearer {slack_token}",
                 "Content-Type": "application/json; charset=utf-8"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        print("slack ok" if resp.get("ok") else f"slack error: {resp.get('error')}")
    except Exception as e:  # noqa: BLE001
        print(f"slack post failed (non-fatal): {e}")
else:
    print("no thread ts or slack creds; skipping Slack notify")
