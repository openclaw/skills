---
name: ringbot
description: Make outbound AI phone calls. Use when asked to call a business, make a phone call, order food by phone, schedule appointments, or any task requiring voice calls. Triggers on "call", "phone", "dial", "ring", "order pizza", "make reservation", "schedule appointment".
---

# RingBot - AI Phone Calls

Make outbound phone calls with an AI voice agent that can have natural conversations.

## 💰 Why RingBot? (99% Cheaper Voice AI)

**Traditional Voice AI costs:** $0.10-0.50/minute (ElevenLabs, PlayHT, etc.)
**RingBot costs:** ~$0.01/minute (just Twilio phone costs!)

| Component | Provider | Cost |
|-----------|----------|------|
| STT (Speech-to-Text) | Groq Whisper | **FREE** |
| LLM (AI Brain) | Groq Llama 3.3 70B | **FREE** |
| TTS (Text-to-Speech) | Groq Orpheus | **FREE** |
| Voice Infrastructure | LiveKit Cloud | **FREE tier** |
| Phone Calls | Twilio | ~$0.01/min |

**You only pay for actual phone minutes through Twilio.**

## 📦 Two Ways to Use RingBot

### Option 1: DIY (Free - Bring Your Own Keys)

Set up your own infrastructure - **completely free** except Twilio phone costs.

**Required accounts:**

1. **Twilio** - https://twilio.com
   - Phone number (~$1/month) + calls (~$0.01/min)
   - Get: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`

2. **LiveKit Cloud** - https://cloud.livekit.io (free tier)
   - Create project + SIP trunk connected to Twilio
   - Get: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `LIVEKIT_SIP_TRUNK_ID`

3. **Groq** - https://console.groq.com (100% free)
   - Get API key + **accept TTS terms**: https://console.groq.com/playground?model=canopylabs%2Forpheus-v1-english
   - Get: `GROQ_API_KEY`

```bash
# .env for DIY setup
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_SIP_TRUNK_ID=your_trunk_id
GROQ_API_KEY=your_groq_key
```

### Option 2: Hosted (Paid - Just Bring Twilio)

Don't want to set up LiveKit and Groq? Use our hosted infrastructure.

- ✅ No LiveKit setup needed
- ✅ No Groq setup needed  
- ✅ Just connect your Twilio account
- 💰 Pay per minute + rate limits apply

**Coming soon** - Contact for early access: https://talkforceai.com

## 🚀 Use Cases

### 1. Order Food by Phone
> "Call DeLuca's Pizza and order a large pepperoni for pickup under Greg"

### 2. Make Reservations
> "Call the restaurant and make a reservation for 4 people Saturday at 7pm"

### 3. Schedule Appointments
> "Call Dr. Smith's office and schedule my annual checkup for next week morning"

### 4. Customer Service Calls
> "Call Comcast and ask about upgrading my internet plan"

### 5. Personal Messages
> "Call mom and tell her I love her and ask how her day was"

### 6. Business Lead Qualification
> "Call this list of leads and ask if they're interested in our parking solutions"

### 7. Automated Daily Calls
> "Every morning at 9am, call the warehouse and check inventory status"

### 8. Appointment Reminders
> "Call patients and remind them of their appointments tomorrow"

## Making a Call

```bash
curl -X POST http://localhost:8000/ringbot/call \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1XXXXXXXXXX",
    "purpose": "Brief description of call objective",
    "context": "Additional context the AI should know"
  }'
```

**Parameters:**
- `to` - Phone number in E.164 format (+1XXXXXXXXXX)
- `purpose` - What the call is about (guides AI behavior)
- `context` - Background info, specific requests, what to collect

## Example: Order Pizza

**Step 1: Find the restaurant**
```bash
goplaces search "pizza" --lat 41.36 --lng="-72.56" --limit 3
```

**Step 2: Get phone number**
```bash
goplaces details ChIJRdQwYs4v5okRY2gp8pgskJ0
# Phone: (860) 663-3999
```

**Step 3: Make the call**
```bash
curl -X POST http://localhost:8000/ringbot/call \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+18606633999",
    "purpose": "Order a pizza for pickup",
    "context": "Order: 1 large pepperoni pizza. Customer name: Greg. Ask for pickup time and total."
  }'
```

## Tips for Good Results

**Purpose** - Keep it to one clear sentence:
- ✅ "Order a pizza for pickup"
- ✅ "Schedule a dental cleaning"
- ❌ "Call them and maybe order something or ask questions"

**Context** - Be specific:
- Customer/caller name
- Exact order or request
- Preferences and constraints
- What info to collect back

## Service Management

**Start the agent:**
```bash
cd /path/to/ringbot/src && python agent.py start
```

**Start the API:**
```bash
cd /path/to/ringbot && python main.py
```

**Check call status:**
```bash
curl http://localhost:8000/ringbot/call/{call_id}
```
