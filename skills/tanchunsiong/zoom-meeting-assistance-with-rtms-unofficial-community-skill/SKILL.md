---
name: zoom-meeting-assistance-rtms-unofficial-community
description: Zoom RTMS Meeting Assistant — start on-demand to capture meeting audio, video, transcript, screenshare, and chat via Zoom Real-Time Media Streams. Handles meeting.rtms_started and meeting.rtms_stopped webhook events. Provides AI-powered dialog suggestions, sentiment analysis, and live summaries with WhatsApp notifications. Use when a Zoom RTMS webhook fires or the user asks to record/analyze a meeting.
---

# Zoom RTMS Meeting Assistant

Headless capture service for Zoom meetings using Real-Time Media Streams (RTMS). Receives webhook events, connects to RTMS WebSockets, records all media, and runs AI analysis via Clawdbot.

## Webhook Events Handled

This skill processes two Zoom webhook events:

- **`meeting.rtms_started`** — Zoom sends this when RTMS is activated for a meeting. Contains `server_urls`, `rtms_stream_id`, and `meeting_uuid` needed to connect to the RTMS WebSocket.
- **`meeting.rtms_stopped`** — Zoom sends this when RTMS ends (meeting ended or RTMS disabled). Triggers cleanup: closes WebSocket connections, generates screenshare PDF, sends summary notification.

## Webhook Dependency

This skill needs a public webhook endpoint to receive these events from Zoom.

**Preferred:** Use the **ngrok-unofficial-webhook-skill** (`skills/ngrok-unofficial-webhook-skill`). It auto-discovers this skill via `webhookEvents` in `skill.json`, notifies the user, and offers to route events here.

Other webhook solutions (e.g. custom servers, cloud functions) will work but require additional integration to forward payloads to this service.

## Prerequisites

```bash
cd skills/zoom-meeting-assistance-rtms-unofficial-community
npm install
```

Requires `ffmpeg` for post-meeting media conversion.

## Environment Variables

Set these in the skill's `.env` file:

**Required:**
- `ZOOM_SECRET_TOKEN` — Zoom webhook secret token
- `ZOOM_CLIENT_ID` — Zoom app Client ID
- `ZOOM_CLIENT_SECRET` — Zoom app Client Secret

**Optional:**
- `PORT` — Server port (default: `3000`; skill uses `4048` via `forwardPort` in `skill.json`)
- `WEBHOOK_PATH` — Webhook endpoint path (default: `/webhook`)
- `WEBSOCKET_URL` — Public URL for RTMS signaling (e.g. ngrok URL)
- `AI_PROVIDER` — AI provider: `openrouter`, `gemma`, `qwen`, `deepseek` (default: `gemma`)
- `AI_PROCESSING_INTERVAL_MS` — AI analysis frequency in ms (default: `30000`)
- `AI_FUNCTION_STAGGER_MS` — Delay between AI calls in ms (default: `5000`)
- `OPENROUTER_API_KEY` — Required if `AI_PROVIDER=openrouter`
- `OPENROUTER_MODEL` — Model to use (default: `google/gemini-2.5-pro`)
- `AUDIO_DATA_OPT` — `1` = mixed stream, `2` = multi-stream (default: `2`)
- `CLAWDBOT_NOTIFY_CHANNEL` — Notification channel (default: `whatsapp`)
- `CLAWDBOT_NOTIFY_TARGET` — Phone number / target for notifications

## Starting the Service

```bash
cd skills/zoom-meeting-assistance-rtms-unofficial-community
node index.js
```

This starts an Express server listening for Zoom webhook events on `PORT`.

**Typical flow:**
1. Start the server as a background process
2. Zoom sends `meeting.rtms_started` webhook → service connects to RTMS WebSocket
3. Media streams in real-time: audio, video, transcript, screenshare, chat
4. AI processing runs periodically (dialog suggestions, sentiment, summary)
5. `meeting.rtms_stopped` → service closes connections, generates screenshare PDF

## Recorded Data

All recordings are stored at:
```
skills/zoom-meeting-assistance-rtms-unofficial-community/recordings/{streamId}/
```

Each stream folder contains:

| File | Content | Searchable |
|------|---------|-----------|
| `transcript.txt` | Plain text transcript with timestamps and speaker names | ✅ Best for searching — grep-friendly, one line per utterance |
| `transcript.vtt` | VTT format transcript with timing cues | ✅ |
| `transcript.srt` | SRT format transcript | ✅ |
| `events.log` | Participant join/leave, active speaker changes (JSON lines) | ✅ |
| `chat.txt` | Chat messages with timestamps | ✅ |
| `ai_summary.md` | AI-generated meeting summary (markdown) | ✅ Key document — read this first for meeting overview |
| `ai_dialog.json` | AI dialog suggestions | ✅ |
| `ai_sentiment.json` | Sentiment analysis per participant | ✅ |
| `{userId}.raw` | Per-participant raw PCM audio | ❌ Binary |
| `combined.h264` | Raw H.264 video | ❌ Binary |
| `processed/screenshare.pdf` | Deduplicated screenshare frames as PDF | ❌ Binary |

Post-meeting summaries may also be saved to:
```
skills/zoom-meeting-assistance-rtms-unofficial-community/meeting_summary/
```

## Searching & Querying Past Meetings

To find and review past meeting data:

```bash
# List all recorded meetings
ls recordings/

# Search across all transcripts for a keyword
grep -rl "keyword" recordings/*/transcript.txt

# Search for what a specific person said
grep "Chun Siong Tan" recordings/*/transcript.txt

# Read a meeting summary
cat recordings/<streamId>/ai_summary.md

# Search summaries for a topic
grep -rl "topic" recordings/*/ai_summary.md

# Check who attended a meeting
cat recordings/<streamId>/events.log

# Get sentiment for a meeting
cat recordings/<streamId>/ai_sentiment.json
```

The `.txt`, `.md`, `.json`, and `.log` files are all text-based and searchable. Start with `ai_summary.md` for a quick overview, then drill into `transcript.txt` for specific quotes or details.

## API Endpoints

```bash
# Toggle WhatsApp notifications on/off
curl -X POST http://localhost:3000/api/notify-toggle -H "Content-Type: application/json" -d '{"enabled": false}'

# Check notification status
curl http://localhost:3000/api/notify-toggle
```

## Post-Meeting Helpers

These scripts are NOT auto-triggered. Run manually after meeting ends:

```bash
# Convert raw audio/video to WAV/MP4
node convertMeetingMedia.js <streamId>

# Mux first audio + video into final MP4
node muxFirstAudioVideo.js <streamId>
```

## Reading Meeting Data

After or during a meeting, read files from `recordings/{streamId}/`:

```bash
# List recorded meetings
ls recordings/

# Read transcript
cat recordings/<streamId>/transcript.txt

# Read AI summary
cat recordings/<streamId>/ai_summary.md

# Read sentiment analysis
cat recordings/<streamId>/ai_sentiment.json
```

## Prompt Customization

Edit these files to change AI behavior:
- `summary_prompt.md` — Meeting summary generation
- `query_prompt.md` — Query response formatting
- `query_prompt_current_meeting.md` — Real-time meeting analysis
- `query_prompt_dialog_suggestions.md` — Dialog suggestion style
- `query_prompt_sentiment_analysis.md` — Sentiment scoring logic
