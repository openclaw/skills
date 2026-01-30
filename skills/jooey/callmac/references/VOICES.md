# Edge TTS Voices Reference

Complete list of available Microsoft Edge TTS neural voices.

## How to List Voices

```bash
python3 -m edge_tts --list-voices
```

## Recommended Voices

### English (United States)
- `en-US-JennyNeural` - **Recommended**: Friendly, considerate, comfortable (General)
- `en-US-AriaNeural` - Positive, confident (News, Novel)
- `en-US-AvaNeural` - Expressive, caring, pleasant (Conversation, Copilot)
- `en-US-EmmaNeural` - Cheerful, clear, conversational (Conversation, Copilot)
- `en-US-MichelleNeural` - Friendly, pleasant (News, Novel)

### Chinese (Mandarin, China)
- `zh-CN-XiaoxiaoNeural` - **Recommended**: Warm (News, Novel)
- `zh-CN-XiaoyiNeural` - Lively (Cartoon, Novel)
- `zh-CN-liaoning-XiaobeiNeural` - Humorous (Dialect)
- `zh-CN-shaanxi-XiaoniNeural` - Bright (Dialect)

### Chinese (Taiwan)
- `zh-TW-HsiaoChenNeural` - Warm (News, Novel)
- `zh-TW-HsiaoYuNeural` - Lively (Cartoon, Novel)
- `zh-TW-YunJheNeural` - Calm (General)

### Multilingual Voices
- `en-US-AvaMultilingualNeural` - Expressive, caring, pleasant (Conversation, Copilot)
- `en-US-EmmaMultilingualNeural` - Cheerful, clear, conversational (Conversation, Copilot)

## Complete Voice List by Language

### English Variants
```
en-US-AnaNeural                    Female    Cartoon, Conversation  Cute
en-US-AriaNeural                   Female    News, Novel            Positive, Confident
en-US-AvaMultilingualNeural        Female    Conversation, Copilot  Expressive, Caring, Pleasant, Friendly
en-US-AvaNeural                    Female    Conversation, Copilot  Expressive, Caring, Pleasant, Friendly
en-US-EmmaMultilingualNeural       Female    Conversation, Copilot  Cheerful, Clear, Conversational
en-US-EmmaNeural                   Female    Conversation, Copilot  Cheerful, Clear, Conversational
en-US-JennyNeural                  Female    General                Friendly, Considerate, Comfort
en-US-MichelleNeural               Female    News, Novel            Friendly, Pleasant
en-US-GuyNeural                    Male      News, Novel            Confident, Authoritative
en-US-RyanNeural                   Male      General                Calm, Soothing
```

### Chinese Variants
```
zh-CN-XiaoxiaoNeural               Female    News, Novel            Warm
zh-CN-XiaoyiNeural                 Female    Cartoon, Novel         Lively
zh-CN-YunjianNeural                Male      News, Novel            Calm, Authoritative
zh-CN-YunxiNeural                  Male      Cartoon, Novel         Friendly, Energetic
zh-CN-liaoning-XiaobeiNeural       Female    Dialect                Humorous
zh-CN-shaanxi-XiaoniNeural         Female    Dialect                Bright

zh-TW-HsiaoChenNeural              Female    News, Novel            Warm
zh-TW-HsiaoYuNeural                Female    Cartoon, Novel         Lively
zh-TW-YunJheNeural                 Male      General                Calm
```

### Other Popular Languages

#### Japanese
```
ja-JP-NanamiNeural                 Female    Conversation, Copilot  Cheerful, Friendly
ja-JP-KeitaNeural                  Male      General                Calm, Soothing
```

#### Korean
```
ko-KR-SunHiNeural                  Female    General                Friendly, Calm
ko-KR-InJoonNeural                 Male      General                Authoritative, Clear
```

#### French
```
fr-FR-DeniseNeural                 Female    News, Novel            Elegant, Clear
fr-FR-HenriNeural                  Male      General                Calm, Authoritative
```

#### German
```
de-DE-KatjaNeural                  Female    General                Friendly, Clear
de-DE-ConradNeural                 Male      General                Authoritative, Calm
```

#### Spanish
```
es-ES-ElviraNeural                 Female    General                Friendly, Clear
es-ES-AlvaroNeural                 Male      General                Calm, Authoritative
es-MX-DaliaNeural                  Female    General                Friendly, Warm
```

## Voice Selection Guidelines

### By Use Case

1. **Announcements/Notifications**: Use clear, confident voices
   - English: `en-US-AriaNeural`, `en-US-MichelleNeural`
   - Chinese: `zh-CN-XiaoxiaoNeural`, `zh-TW-HsiaoChenNeural`

2. **Conversational/Assistant**: Use friendly, warm voices
   - English: `en-US-JennyNeural`, `en-US-AvaNeural`
   - Chinese: `zh-CN-XiaoyiNeural`, `zh-TW-HsiaoYuNeural`

3. **Educational/Instructional**: Use clear, calm voices
   - English: `en-US-RyanNeural`, `en-US-EmmaNeural`
   - Chinese: `zh-CN-YunjianNeural`, `zh-TW-YunJheNeural`

4. **Entertainment/Storytelling**: Use expressive, lively voices
   - English: `en-US-AnaNeural`, `en-US-GuyNeural`
   - Chinese: `zh-CN-liaoning-XiaobeiNeural`, `zh-CN-shaanxi-XiaoniNeural`

### By Language Mix

For mixed Chinese/English content:
- **English segments**: `en-US-JennyNeural` (friendly) or `en-US-AriaNeural` (confident)
- **Chinese segments**: `zh-CN-XiaoxiaoNeural` (warm) or `zh-CN-XiaoyiNeural` (lively)

### Voice Characteristics

- **Neural vs Standard**: Neural voices are higher quality but may require more processing time
- **Gender**: Choose based on preference and context
- **Style**: Match voice style to content type (news, conversation, cartoon, etc.)
- **Multilingual**: Some voices handle multiple languages well

## Testing Voices

To test a specific voice:

```bash
python3 -m edge_tts --voice "en-US-JennyNeural" --text "Hello, this is a test" --write-media test.mp3
afplay test.mp3
```

## Notes

- Edge TTS voices require internet connection
- Neural voices provide highest quality but may have latency
- Some voices support SSML for advanced control
- Voice availability may vary by region
- For offline use, consider system TTS alternatives