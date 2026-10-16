# Approved Action Contracts

The autonomous command center accepts an optional explicit `action` envelope. An action always requires human approval, regardless of model risk classification.

## Gmail send

```json
{
  "task": "Draft and send a concise project update.",
  "action": {
    "type": "gmail_send",
    "payload": {
      "to": "recipient@example.com",
      "subject": "Project update",
      "body": "Optional explicit body. If omitted and the communications specialist produced a draft, that draft is placed into the approval preview.",
      "email_type": "text"
    }
  }
}
```

## Calendar create

```json
{
  "task": "Create the approved project review meeting.",
  "action": {
    "type": "calendar_create",
    "payload": {
      "calendar_id": "name@example.com",
      "start": "2026-10-20T10:00:00+03:00",
      "end": "2026-10-20T11:00:00+03:00",
      "summary": "Project review",
      "description": "Quarterly project review"
    }
  }
}
```

## Drive create from text

```json
{
  "task": "Archive this approved note in Drive.",
  "action": {
    "type": "drive_create_text",
    "payload": {
      "name": "project-note.txt",
      "content": "Approved text content"
    }
  }
}
```

## Telegram notify

```json
{
  "task": "Send this approved operator notification.",
  "action": {
    "type": "telegram_notify",
    "payload": {
      "chat_id": "123456789",
      "text": "Approved notification text"
    }
  }
}
```

## Approval

When an action is present, the command center returns HTTP 202 with an execution-specific `approval_url`. Review the entire `preview`, then POST:

```json
{"approved": true, "note": "Reviewed"}
```

or reject with:

```json
{"approved": false, "note": "Do not execute"}
```

The URL expires after the configured wait interval (24 hours in the provided workflow).
