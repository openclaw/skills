# Zoom RTMS Meeting Assistant

Headless capture service for Zoom meetings using Real-Time Media Streams (RTMS). Receives webhook events, connects to RTMS WebSockets, records all media, and runs AI analysis via Clawdbot with WhatsApp notifications.

> **Unofficial** — This skill is not affiliated with or endorsed by Zoom Video Communications.

## Features

- **Real-time capture** — Audio, video, transcript, screenshare, and chat via RTMS WebSockets
- **AI analysis** — Dialog suggestions, sentiment analysis, and live summaries via Clawdbot
- **WhatsApp notifications** — Real-time AI results sent via WhatsApp
- **Multi-format transcripts** — VTT, SRT, and plain text with timestamps and speaker names
- **Screenshare PDF** — Deduplicated screenshare frames compiled into a PDF
- **Per-participant audio** — Raw PCM audio per participant with gap filling
- **Notification toggle** — Mute/unmute notifications mid-meeting via API

## How It Works

1. **Receive webhook** — Zoom sends `meeting.rtms_started` via the [ngrok webhook skill](https://github.com/tanchunsiong/ngrok-unofficial-webhook-skill)
2. **Connect to RTMS** — Service connects to Zoom's RTMS WebSocket using the provided stream URLs
3. **Capture media** — All streams saved in real-time to `recordings/{streamId}/`
4. **AI processing** — Clawdbot periodically analyzes transcripts for dialog suggestions, sentiment, and summaries
5. **Meeting ends** — `meeting.rtms_stopped` triggers cleanup, PDF generation, and summary notification

## Quick Start

### 1. Install dependencies

```bash
cd skills/zoom-meeting-assistance-rtms-unofficial-community
npm install
```

Requires `ffmpeg` for post-meeting media conversion.

### 2. Configure

Copy `.env.example` to `.env` and fill in:

```env
ZOOM_SECRET_TOKEN=your_webhook_secret_token
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
CLAWDBOT_NOTIFY_TARGET=+1234567890
```

### 3. Start

```bash
node index.js
```

The service listens on port 4048 (configurable) for webhook events forwarded by the ngrok skill.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ZOOM_SECRET_TOKEN` | ✅ | — | Zoom webhook secret token |
| `ZOOM_CLIENT_ID` | ✅ | — | Zoom app Client ID |
| `ZOOM_CLIENT_SECRET` | ✅ | — | Zoom app Client Secret |
| `PORT` | — | `3000` | Express server port |
| `WEBHOOK_PATH` | — | `/webhook` | Webhook endpoint path |
| `AI_PROCESSING_INTERVAL_MS` | — | `30000` | AI analysis frequency (ms) |
| `AI_FUNCTION_STAGGER_MS` | — | `5000` | Delay between AI calls (ms) |
| `CLAWDBOT_BIN` | — | `clawdbot` | Path to Clawdbot binary |
| `CLAWDBOT_NOTIFY_CHANNEL` | — | `whatsapp` | Notification channel |
| `CLAWDBOT_NOTIFY_TARGET` | — | — | Phone number / target |
| `CLAWDBOT_TIMEOUT` | — | `120` | Clawdbot timeout (seconds) |
| `AUDIO_DATA_OPT` | — | `2` | `1` = mixed audio, `2` = multi-stream |

## Recorded Data

All recordings stored at `recordings/{streamId}/`:

| File | Content |
|------|---------|
| `transcript.txt` | Plain text transcript — best for searching |
| `transcript.vtt` | VTT format transcript with timing cues |
| `transcript.srt` | SRT format transcript |
| `events.log` | Participant join/leave, active speaker (JSON lines) |
| `chat.txt` | Chat messages with timestamps |
| `ai_summary.md` | AI-generated meeting summary |
| `ai_dialog.json` | AI dialog suggestions |
| `ai_sentiment.json` | Sentiment analysis per participant |
| `{userId}.raw` | Per-participant raw PCM audio |
| `combined.h264` | Raw H.264 video |
| `processed/screenshare.pdf` | Deduplicated screenshare frames as PDF |

## Searching Past Meetings

```bash
# List all recorded meetings
ls recordings/

# Search across all transcripts
grep -rl "keyword" recordings/*/transcript.txt

# Search what a specific person said
grep "Name" recordings/*/transcript.txt

# Read a meeting summary
cat recordings/<streamId>/ai_summary.md

# Check who attended
cat recordings/<streamId>/events.log
```

## API Endpoints

```bash
# Toggle WhatsApp notifications on/off
curl -X POST http://localhost:3000/api/notify-toggle \
  -H "Content-Type: application/json" -d '{"enabled": false}'

# Check notification status
curl http://localhost:3000/api/notify-toggle
```

## Post-Meeting Helpers

Run manually after a meeting ends:

```bash
# Convert raw audio/video to WAV/MP4
node convertMeetingMedia.js <streamId>

# Mux first audio + video into final MP4
node muxFirstAudioVideo.js <streamId>
```

## Prompt Customization

Edit these files to change AI behavior:
- `summary_prompt.md` — Meeting summary generation
- `query_prompt.md` — Query response formatting
- `query_prompt_current_meeting.md` — Real-time meeting analysis
- `query_prompt_dialog_suggestions.md` — Dialog suggestion style
- `query_prompt_sentiment_analysis.md` — Sentiment scoring logic

## File Structure

```
├── .env                        # API keys & config
├── index.js                    # Main RTMS server & recording logic
├── chatWithClawdbot.js         # Clawdbot AI integration
├── convertMeetingMedia.js      # FFmpeg conversion helper
├── muxFirstAudioVideo.js       # Audio/video muxing helper
├── saveRawAudioAdvance.js      # Real-time audio stream saving
├── saveRawVideoAdvance.js      # Real-time video stream saving
├── writeTranscriptToVtt.js     # Transcript writing (VTT/SRT/TXT)
├── saveSharescreen.js          # Screenshare capture & PDF generation
├── summary_prompt.md           # Summary generation prompt
├── query_prompt*.md            # AI query prompts
└── recordings/                 # Meeting data storage
    └── {streamId}/             # Per-meeting directory
```

## Related Skills

- **[ngrok-unofficial-webhook-skill](https://github.com/tanchunsiong/ngrok-unofficial-webhook-skill)** — Public webhook endpoint (required to receive Zoom events)
- **[zoom-unofficial-community-skill](https://github.com/tanchunsiong/zoom-unofficial-community-skill)** — Zoom REST API CLI (can start/stop RTMS via `meetings rtms-start/stop`)

## Bug Reports & Contributing

Found a bug? Please raise an issue at:
👉 https://github.com/tanchunsiong/zoom-meeting-assistance-with-rtms-unofficial-community-skill/issues

Pull requests are also welcome!

## License

MIT
