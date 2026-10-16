# Discord Relay Contract

n8n currently provides a native Discord output node but no native Discord Trigger. Directly exposing an unsigned generic webhook as a Discord operator surface would be a weak trust boundary.

The repository therefore uses:

`Discord -> signature-verifying relay -> Header-Auth n8n webhook -> command center -> native Discord reply`

## Relay responsibility

The relay must:

1. receive the Discord event/interaction;
2. verify Discord authenticity using the application's public key and Discord's signature headers;
3. reject stale/replayed/invalid requests;
4. normalize an operator message;
5. call the n8n relay webhook using a separate high-entropy Header Auth secret.

n8n does **not** trust a caller merely because the body looks like Discord.

## Normalized body

```json
{
  "relay_version": "1",
  "message_id": "123456789012345678",
  "user_id": "123456789012345678",
  "channel_id": "123456789012345678",
  "content": "research current n8n orchestration patterns",
  "bot": false
}
```

The n8n gateway also enforces explicit user/channel allowlists.

## Action syntax

The relay can forward an explicit action command unchanged:

```text
!action {"type":"github_issue_create","payload":{"owner":"OWNER","repo":"REPO","title":"Title","body":"Body"}}
```

The command center still returns an approval request. The gateway never bypasses human approval.
