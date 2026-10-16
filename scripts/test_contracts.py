#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def load(rel):
    p = ROOT / rel
    if not p.exists():
        errors.append(f"missing {rel}")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{rel}: {exc}")
        return {}

def node_by_name(wf, name):
    for n in wf.get("nodes", []):
        if n.get("name") == name:
            return n
    return None

ACTIONS = {
    "gmail_send","calendar_create","drive_create_text","telegram_notify",
    "slack_notify","discord_notify","github_issue_create","github_issue_comment",
    "github_file_create","github_file_update",
}

cc = load("workflows/autonomous/00-autonomous-command-center.json")
deliberation = load("workflows/autonomous/40-deliberation-review.json")
dispatcher = load("workflows/actions/50-approved-action-dispatcher.json")
gh = load("workflows/actions/57-github-write-approved.json")
slack = load("workflows/operators/61-slack-command-gateway.json")
discord = load("workflows/operators/62-discord-relay-command-gateway.json")
pgmem = load("workflows/storage/06-postgres-memory-store.json")
pgledger = load("workflows/storage/56-postgres-action-ledger.json")
daily = load("workflows/schedules/70-daily-autonomous-brief.json")

cc_text = json.dumps(cc)
disp_text = json.dumps(dispatcher)

for a in ACTIONS:
    if a not in cc_text:
        errors.append(f"command center missing action contract {a}")
    if a not in disp_text:
        errors.append(f"dispatcher missing action contract {a}")

wait = node_by_name(cc, "Wait for Human Approval")
if not wait or wait.get("parameters", {}).get("incomingAuthentication") != "headerAuth":
    errors.append("command center approval Wait node must use Header Auth")

mark = node_by_name(dispatcher, "Mark Action Complete")
if not mark:
    errors.append("dispatcher missing completion write")
else:
    key_expr = json.dumps(mark.get("parameters", {}))
    if "Restore Claimed Action" not in key_expr or "action_key" not in key_expr:
        errors.append("dispatcher completion must use original claimed action_key")

gh_http = [n for n in gh.get("nodes", []) if n.get("type") == "n8n-nodes-base.httpRequest"]
if len(gh_http) != 4:
    errors.append("GitHub write adapter must expose exactly four fixed HTTP operations")
for n in gh_http:
    url = str(n.get("parameters", {}).get("url", ""))
    if not url.startswith("=https://api.github.com/repos/"):
        errors.append(f"GitHub write node {n.get('name')} must be pinned to api.github.com/repos")
    if n.get("retryOnFail") is True:
        errors.append(f"GitHub non-idempotent write node {n.get('name')} must not auto-retry")

slack_trigger = next((n for n in slack.get("nodes", []) if n.get("type") == "n8n-nodes-base.slackTrigger"), None)
if not slack_trigger:
    errors.append("Slack gateway must use native Slack Trigger")

discord_webhook = next((n for n in discord.get("nodes", []) if n.get("type") == "n8n-nodes-base.webhook"), None)
if not discord_webhook or discord_webhook.get("parameters", {}).get("authentication") != "headerAuth":
    errors.append("Discord relay gateway must require Header Auth")

def input_names(wf):
    for n in wf.get("nodes", []):
        if n.get("type") == "n8n-nodes-base.executeWorkflowTrigger":
            vals = n.get("parameters", {}).get("workflowInputs", {}).get("values", [])
            return {v.get("name") for v in vals}
    return set()

if input_names(pgmem) != {"operation","request_id","key","value","limit"}:
    errors.append("Postgres memory store does not preserve memory workflow input contract")
if input_names(pgledger) != {"operation","key","value"}:
    errors.append("Postgres action ledger does not preserve ledger input contract")

# Deliberation is a review-only module: exactly two model calls, both pinned to OpenAI Responses,
# and no provider write nodes or sub-workflow side-effect dispatch.
deliberation_http = [n for n in deliberation.get("nodes", []) if n.get("type") == "n8n-nodes-base.httpRequest"]
if len(deliberation_http) != 2:
    errors.append("deliberation review must contain exactly two model HTTP calls")
for n in deliberation_http:
    if n.get("parameters", {}).get("url") != "https://api.openai.com/v1/responses":
        errors.append(f"deliberation HTTP node {n.get('name')} is not pinned to OpenAI Responses")
write_types = {
    "n8n-nodes-base.gmail","n8n-nodes-base.googleCalendar","n8n-nodes-base.googleDrive",
    "n8n-nodes-base.telegram","n8n-nodes-base.slack","n8n-nodes-base.discord",
    "n8n-nodes-base.github","n8n-nodes-base.postgres","n8n-nodes-base.executeWorkflow",
}
for n in deliberation.get("nodes", []):
    if n.get("type") in write_types:
        errors.append(f"deliberation review contains side-effect-capable node {n.get('name')}")

if input_names(deliberation) != {"request_id","task","context","candidate","model"}:
    errors.append("deliberation review input contract drifted")

daily_text = json.dumps(daily).lower()
if '"action"' in daily_text and "requested action" not in daily_text:
    errors.append("daily read-only job unexpectedly contains an action envelope")

if errors:
    for e in errors:
        print("ERROR:", e, file=sys.stderr)
    sys.exit(1)
print("Contract tests passed")
