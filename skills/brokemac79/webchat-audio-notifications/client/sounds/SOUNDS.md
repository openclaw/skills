# Sound Files Attribution

All sound files in this directory are royalty-free and free for commercial use.

## Sound Intensity Levels

We provide 5 notification sounds at different intensity levels:

### Level 1 - Whisper (9.5KB)
- **Source:** Mixkit.co
- **License:** Mixkit Free License
- **Description:** Most subtle, barely noticeable
- **Use case:** When you want minimal distraction
- **File:** level1.mp3

### Level 2 - Soft (12KB)
- **Source:** Mixkit.co
- **License:** Mixkit Free License
- **Description:** Gentle chime, polite notification
- **Use case:** Quiet environments, regular messages
- **File:** level2.mp3

### Level 3 - Medium (13KB) - DEFAULT
- **Source:** Mixkit.co
- **License:** Mixkit Free License
- **Description:** Balanced, clear but not aggressive
- **Use case:** Standard notification sound
- **File:** level3.mp3

### Level 4 - Loud (43KB)
- **Source:** Mixkit.co
- **License:** Mixkit Free License
- **Description:** Attention-getting, prominent
- **Use case:** Important notifications, mentions
- **File:** level4.mp3

### Level 5 - Very Loud (63KB)
- **Source:** Mixkit.co
- **License:** Mixkit Free License
- **Description:** Impossible to miss, urgent
- **Use case:** Critical alerts, DMs, urgent notifications
- **File:** level5.mp3

## Legacy Files (Backward Compatibility)

### notification.mp3 (13KB)
- Same as level3.mp3
- Kept for backward compatibility

### alert.mp3 (63KB)
- Same as level5.mp3
- Kept for backward compatibility

## License

These sounds are used under the Mixkit Free License which allows:
- ✅ Commercial use
- ✅ Personal projects
- ✅ No attribution required (but appreciated)
- ✅ Modification allowed

Full license: https://mixkit.co/license/#sfxFree

## Usage

In your code:
```javascript
// Use specific level
notifier.setSound('level1');  // Whisper
notifier.setSound('level3');  // Medium (default)
notifier.setSound('level5');  // Very loud

// Or use legacy names
notifier.setSound('notification');  // Same as level3
notifier.setSound('alert');          // Same as level5
```

## Choosing the Right Level

**Level 1 (Whisper)** - Work environments, libraries, sleeping partner nearby  
**Level 2 (Soft)** - General use, office settings  
**Level 3 (Medium)** - Recommended default for most users  
**Level 4 (Loud)** - Noisy environments, important messages  
**Level 5 (Very Loud)** - Critical alerts only, emergency notifications  

## File Sizes

| Level | Size | Duration | Intensity |
|-------|------|----------|-----------|
| 1     | 9.5KB | ~0.7s   | ▁▁▁▁▁ |
| 2     | 12KB  | ~0.9s   | ▂▂▂▂▁ |
| 3     | 13KB  | ~1.0s   | ▃▃▃▂▁ |
| 4     | 43KB  | ~3.3s   | ▅▅▅▅▂ |
| 5     | 63KB  | ~4.9s   | ▇▇▇▇▇ |

## Notes

- All files are MP3 format (MPEG ADTS, layer III, v1, 128 kbps, 44.1 kHz, JntStereo)
- WebM versions not included (MP3 has universal browser support)
- Smaller files = shorter duration and lower perceived volume
- Larger files = longer duration and higher perceived volume
- Total collection size: ~153KB (all 5 levels + legacy files)

## Source URLs

All sounds downloaded from:
- https://mixkit.co/free-sound-effects/notification/
- https://mixkit.co/free-sound-effects/alerts/

Sound IDs (for reference):
- Level 1: Mixkit #2356
- Level 2: Mixkit #2357
- Level 3: Mixkit #2354
- Level 4: Mixkit #2867
- Level 5: Mixkit #2869
