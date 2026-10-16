# Approved Action Contracts

Every action below requires the command center's human approval path before the deterministic dispatcher can run it.

## Existing providers

### Gmail
`gmail_send`

```json
{"type":"gmail_send","payload":{"to":"recipient@example.com","subject":"Project update","body":"Approved body","email_type":"text"}}
```

### Google Calendar
`calendar_create`

```json
{"type":"calendar_create","payload":{"calendar_id":"name@example.com","start":"2026-10-20T10:00:00+03:00","end":"2026-10-20T11:00:00+03:00","summary":"Project review","description":"Quarterly review"}}
```

### Google Drive
`drive_create_text`

```json
{"type":"drive_create_text","payload":{"name":"project-note.txt","content":"Approved text"}}
```

### Telegram
`telegram_notify`

```json
{"type":"telegram_notify","payload":{"chat_id":"123456789","text":"Approved notification"}}
```

### Slack
`slack_notify`

```json
{"type":"slack_notify","payload":{"channel_id":"C0123456789","text":"Approved notification"}}
```

### Discord
`discord_notify`

```json
{"type":"discord_notify","payload":{"channel_id":"123456789012345678","text":"Approved notification"}}
```

## GitHub write actions

GitHub writes use a separate approved adapter pinned to `api.github.com/repos/...`. The adapter does not accept an arbitrary URL.

### Create issue
`github_issue_create`

```json
{"type":"github_issue_create","payload":{"owner":"OWNER","repo":"REPO","title":"Issue title","body":"Issue body"}}
```

### Create issue/PR conversation comment
`github_issue_comment`

GitHub exposes issue and pull-request conversation comments through the issue-comments REST endpoint.

```json
{"type":"github_issue_comment","payload":{"owner":"OWNER","repo":"REPO","issue_number":123,"body":"Approved comment"}}
```

### Create file
`github_file_create`

```json
{"type":"github_file_create","payload":{"owner":"OWNER","repo":"REPO","path":"docs/note.md","message":"Add note","content":"File contents","branch":"main"}}
```

### Update file
`github_file_update`

The current blob SHA is mandatory. This is an optimistic-concurrency guard: if the file changed after review, GitHub rejects the update instead of silently overwriting newer work.

```json
{"type":"github_file_update","payload":{"owner":"OWNER","repo":"REPO","path":"docs/note.md","message":"Update note","content":"New contents","branch":"main","sha":"0123456789abcdef0123456789abcdef01234567"}}
```

## Approval protocol

When an action is present, the command center returns HTTP 202 and an execution-specific `approval_url`.

Approve:

```json
{"approved":true,"note":"Reviewed"}
```

Reject:

```json
{"approved":false,"note":"Do not execute"}
```

Use the Header Auth credential configured on the Wait node when calling the approval URL.

The URL expires after 24 hours in the provided workflow.

## Operator shortcut

Slack and Discord gateways understand a deliberately explicit operator syntax:

```text
!action {"type":"slack_notify","payload":{"channel_id":"C0123456789","text":"hello"}}
```

This does not bypass approval. It only creates the same explicit action envelope used by API clients.
