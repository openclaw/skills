# Examples and Usage Patterns

Common usage examples for the callmac skill.

## Basic Examples

### Example 1: Simple English Announcement
```bash
# Generate and play English announcement
python3 scripts/generate_tts.py --text "System startup complete" --play

# Save to file
python3 scripts/generate_tts.py --text "Welcome to the application" --output welcome.mp3
```

### Example 2: Simple Chinese Announcement
```bash
# Generate and play Chinese announcement
python3 scripts/generate_tts.py --text "系统启动完成" --play

# With specific Chinese voice
python3 scripts/generate_tts.py --text "欢迎使用本系统" --voice "zh-CN-XiaoyiNeural" --play
```

### Example 3: Mixed Language Announcement
```bash
# Auto-detected mixed language
python3 scripts/generate_tts.py --text "Hello 你好" --play

# With custom voices
python3 scripts/generate_tts.py \
  --text "Welcome 欢迎" \
  --play \
  --voice-en "en-US-AriaNeural" \
  --voice-zh "zh-CN-XiaoxiaoNeural"
```

## Advanced Examples

### Example 4: Loop Playback
```bash
# Play announcement 3 times
python3 scripts/generate_tts.py --text "Reminder: Check your email" --play --loops 3

# Play with volume control
python3 scripts/generate_tts.py --text "Time for meeting" --play --loops 5 --volume 80
```

### Example 5: Scheduled Announcements
```bash
# Create announcement file
python3 scripts/generate_tts.py \
  --text "Daily standup meeting in 5 minutes. 每日站会还有5分钟开始。" \
  --output standup_reminder.mp3

# Schedule with cron (every weekday at 9:55 AM)
echo "55 9 * * 1-5 afplay /path/to/standup_reminder.mp3" | crontab -

# One-time reminder (in 10 minutes)
sleep 600 && afplay /path/to/standup_reminder.mp3 &
```

### Example 6: Multi-part Announcement
```bash
# Create complex announcement with multiple segments
python3 scripts/generate_tts.py \
  --text "Alert: High CPU usage detected. Current usage: 95%. Please check system processes. 警报：检测到高CPU使用率。当前使用率：95%。请检查系统进程。" \
  --play \
  --voice-en "en-US-AriaNeural" \
  --voice-zh "zh-CN-XiaoxiaoNeural"
```

### Example 7: SSML Advanced Control
```bash
# Create SSML for precise control
cat > announcement.ssml << 'EOF'
<speak>
  <voice name="en-US-JennyNeural">
    Welcome to the system. <break time="500ms"/>
  </voice>
  <voice name="zh-CN-XiaoxiaoNeural">
    欢迎使用本系统。<break time="300ms"/>
  </voice>
  <voice name="en-US-JennyNeural">
    Initialization complete.
  </voice>
</speak>
EOF

python3 scripts/generate_tts.py --ssml "$(cat announcement.ssml)" --play
```

## Real-world Scenarios

### Scenario 1: Home Assistant Announcements
```bash
# Doorbell notification
python3 scripts/generate_tts.py \
  --text "Someone is at the door. 门口有人。" \
  --play \
  --loops 2 \
  --volume 90

# Weather update
python3 scripts/generate_tts.py \
  --text "Today's weather: Sunny, 25 degrees. 今天天气：晴，25度。" \
  --play

# Timer completion
python3 scripts/generate_tts.py \
  --text "Timer complete! 计时器完成！" \
  --play \
  --volume 100
```

### Scenario 2: Office/Workplace Announcements
```bash
# Meeting reminders
python3 scripts/generate_tts.py \
  --text "Team meeting in conference room A. 团队会议在A会议室。" \
  --play \
  --loops 2

# System maintenance
python3 scripts/generate_tts.py \
  --text "System maintenance scheduled for 10 PM. 系统维护安排在晚上10点。" \
  --output maintenance_announcement.mp3

# Emergency alerts
python3 scripts/generate_tts.py \
  --text "Emergency: Fire alarm test. Please proceed to exits. 紧急情况：火警测试。请前往出口。" \
  --play \
  --loops 3 \
  --volume 100
```

### Scenario 3: Educational/Teaching Aids
```bash
# Vocabulary pronunciation
python3 scripts/generate_tts.py \
  --text "Apple. A-P-P-L-E. Apple. 苹果。" \
  --play

# Language learning phrases
phrases=(
  "Good morning. 早上好。"
  "How are you? 你好吗？"
  "Thank you. 谢谢。"
  "Goodbye. 再见。"
)

for phrase in "${phrases[@]}"; do
  python3 scripts/generate_tts.py --text "$phrase" --play
  sleep 2
done
```

### Scenario 4: Accessibility Features
```bash
# Screen reader alternative
python3 scripts/generate_tts.py \
  --text "New email from John: Meeting agenda attached. 新邮件来自John：会议议程已附加。" \
  --play

# Document reading
python3 scripts/generate_tts.py \
  --text "$(cat document.txt | head -5)" \
  --play

# Notification reading
python3 scripts/generate_tts.py \
  --text "Notification: Calendar event 'Team Sync' starting now. 通知：日历事件'团队同步'现在开始。" \
  --play
```

## Integration Examples

### Example 8: Integration with System Monitoring
```bash
#!/bin/bash
# monitor_alert.sh

# Check CPU usage
cpu_usage=$(top -l 1 | grep -E "^CPU" | awk '{print $3}' | tr -d '%')

if (( $(echo "$cpu_usage > 90" | bc -l) )); then
  python3 scripts/generate_tts.py \
    --text "High CPU alert: ${cpu_usage}% usage. 高CPU警报：使用率${cpu_usage}%。" \
    --play \
    --volume 90
fi
```

### Example 9: Integration with Calendar
```bash
#!/bin/bash
# calendar_reminder.sh

next_event=$(icalbuddy -n -ea -nc eventsToday | head -1)

if [ -n "$next_event" ]; then
  python3 scripts/generate_tts.py \
    --text "Next event: ${next_event}. 下一个事件：${next_event}。" \
    --play
fi
```

### Example 10: Integration with Home Automation
```bash
#!/bin/bash
# good_morning_routine.sh

# Get weather
weather=$(curl -s "wttr.in?format=%C+%t")

# Get calendar events
events=$(icalbuddy -n -ea -nc eventsToday | head -3 | tr '\n' ',')

python3 scripts/generate_tts.py \
  --text "Good morning! Today's weather: ${weather}. Upcoming events: ${events}. 早上好！今天天气：${weather}。即将发生的事件：${events}。" \
  --play \
  --volume 70
```

## Script Examples

### Example 11: Batch Processing
```bash
#!/bin/bash
# batch_announcements.sh

# Read announcements from file
while IFS= read -r line; do
  if [ -n "$line" ]; then
    echo "Processing: $line"
    python3 scripts/generate_tts.py --text "$line" --play
    sleep 1
  fi
done < announcements.txt
```

### Example 12: Interactive Announcement Creator
```bash
#!/bin/bash
# interactive_tts.sh

echo "Enter announcement text:"
read -r text

echo "Select language:"
echo "1) English only"
echo "2) Chinese only"
echo "3) Mixed Chinese/English"
read -r choice

case $choice in
  1) voice_en="en-US-JennyNeural"; voice_zh="" ;;
  2) voice_en=""; voice_zh="zh-CN-XiaoxiaoNeural" ;;
  3) voice_en="en-US-JennyNeural"; voice_zh="zh-CN-XiaoxiaoNeural" ;;
  *) echo "Invalid choice"; exit 1 ;;
esac

echo "Number of loops:"
read -r loops

python3 scripts/generate_tts.py \
  --text "$text" \
  --play \
  ${voice_en:+--voice-en "$voice_en"} \
  ${voice_zh:+--voice-zh "$voice_zh"} \
  --loops "$loops"
```

## Testing and Debugging

### Example 13: Voice Testing Script
```bash
#!/bin/bash
# test_voices.sh

# Test all recommended voices
voices=(
  "en-US-JennyNeural:Hello, this is Jenny"
  "en-US-AriaNeural:Hello, this is Aria"
  "zh-CN-XiaoxiaoNeural:你好，我是晓晓"
  "zh-CN-XiaoyiNeural:你好，我是晓伊"
)

for voice_text in "${voices[@]}"; do
  IFS=':' read -r voice text <<< "$voice_text"
  echo "Testing: $voice"
  python3 scripts/generate_tts.py --text "$text" --voice "$voice" --play
  sleep 1
done
```

### Example 14: Audio Quality Test
```bash
#!/bin/bash
# audio_quality_test.sh

# Test different text lengths
texts=(
  "Short"
  "This is a medium length sentence for testing."
  "This is a longer piece of text designed to test how the TTS system handles extended speech synthesis with proper pacing and intonation across multiple sentences and paragraphs."
)

for text in "${texts[@]}"; do
  echo "Testing: ${text:0:50}..."
  python3 scripts/generate_tts.py --text "$text" --play
  sleep 2
done
```

## Best Practices

1. **Keep announcements concise** - 10-20 seconds ideal
2. **Use appropriate volume** - 70-80% for normal, 90-100% for alerts
3. **Limit loops** - 2-3 times for important announcements
4. **Test voices** - Different voices work better for different content
5. **Consider timing** - Avoid late night/early morning announcements
6. **Provide context** - Mixed language helps broader understanding
7. **Save files** - For repeated announcements, save to file
8. **Monitor system load** - TTS generation can be CPU intensive

## Real-world Scenarios (Call-Mac)

### Morning Alarm / Wake-up Call
```bash
# Wake up kids with gentle reminder
python3 scripts/generate_tts.py --text "Good morning! Time to wake up. 早上好！该起床了。" --play --volume 80 --loops 2

# Weekday alarm
python3 scripts/generate_tts.py --text "It's 7:30 AM. Breakfast is ready. 现在是早上7点半，早餐准备好了。" --play
```

### Story Time
```bash
# Tell a short story (mixed language)
python3 scripts/generate_tts.py --text "Once upon a time, there was a little capybara named Karpy. 从前，有一只名叫卡皮的小水豚。" --play --voice-en "en-US-AriaNeural" --voice-zh "zh-CN-XiaoxiaoNeural"
```

### Remote Broadcast
```bash
# Broadcast from your phone when away
python3 scripts/generate_tts.py --text "I'll be home in 30 minutes. 我30分钟后到家。" --play --volume 90

# Important family announcement
python3 scripts/generate_tts.py --text "Dinner is ready! 晚饭准备好了！" --play --loops 3 --volume 85
```

## Notes

- Edge TTS requires internet connection
- First generation may be slower due to model loading
- Audio files are cached locally for faster playback
- Consider using SSML for precise timing and emphasis control
- Test on target playback system for volume levels