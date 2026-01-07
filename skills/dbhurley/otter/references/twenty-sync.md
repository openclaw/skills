# Twenty CRM Integration

Sync Otter.ai transcripts to Twenty CRM as notes on contacts or companies.

## Setup

Set environment variables:
```bash
export TWENTY_API_URL="https://api.your-twenty-instance.com"
export TWENTY_API_TOKEN="your-api-token"
```

## Workflow

### 1. Get Transcript Summary
```bash
uv run skills/otter/scripts/otter.py summary <speech_id>
```

### 2. Sync to Contact
```bash
uv run skills/otter/scripts/otter.py sync-twenty <speech_id> --contact "John Smith"
```

### 3. Sync to Company
```bash
uv run skills/otter/scripts/otter.py sync-twenty <speech_id> --company "Acme Corp"
```

## Agent Integration

When the `sync-twenty` command runs, it outputs JSON that the agent should process:

```json
{
  "action": "sync_to_twenty",
  "title": "Weekly Standup",
  "speech_id": "abc123",
  "transcript_text": "...",
  "contact": "John Smith",
  "company": null
}
```

The agent should then:
1. Summarize the transcript (key points, action items)
2. Find the contact/company in Twenty CRM
3. Create a note with the summary
4. Optionally attach full transcript

## Twenty API Endpoints Used

- `POST /api/notes` - Create note
- `GET /api/people?filter[name]` - Find contact
- `GET /api/companies?filter[name]` - Find company

## Example Note Format

```markdown
## Meeting Summary: Weekly Standup
**Date:** 2026-01-06
**Duration:** 45 minutes
**Participants:** John, Sarah, Mike

### Key Points
- Project timeline on track
- Budget review needed
- New feature request from client

### Action Items
- [ ] John: Send budget proposal by Friday
- [ ] Sarah: Schedule client demo

### Full Transcript
[Attached as separate note or linked to Otter]
```

## Automatic Sync (Cron)

Set up a cron job to check for new transcripts and auto-sync:

```json
{
  "name": "otter-sync",
  "schedule": {"kind": "cron", "expr": "*/30 * * * *"},
  "payload": {
    "kind": "agentTurn",
    "message": "Check Otter for new transcripts. If found, summarize and ask if I should sync to Twenty CRM."
  }
}
```
