---
name: tally
version: 1.0.0
description: Create and edit Tally forms via API. Use when building surveys, feedback forms, or questionnaires programmatically. Supports all question types including text inputs, multiple choice, checkboxes, ratings (via workaround), and more.
---

# Tally Forms API

Create and edit Tally.so forms programmatically via their REST API.

## Authentication

```bash
TALLY_KEY=$(cat ~/.config/tally/api_key)
```

## Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| List forms | GET | `https://api.tally.so/forms` |
| Get form | GET | `https://api.tally.so/forms/{id}` |
| Update form | PATCH | `https://api.tally.so/forms/{id}` |
| Get submissions | GET | `https://api.tally.so/forms/{id}/submissions` |

## Block Structure

Tally forms are composed of **blocks**. Questions require **multiple blocks grouped by `groupUuid`**:

```json
{
  "uuid": "q1-title",
  "type": "TITLE",
  "groupUuid": "group-q1",
  "groupType": "QUESTION",
  "payload": {
    "safeHTMLSchema": [["Question text here", [["tag", "span"]]]]
  }
},
{
  "uuid": "q1-input",
  "type": "INPUT_TEXT",
  "groupUuid": "group-q1",
  "groupType": "QUESTION",
  "payload": {"isRequired": true}
}
```

**Key:** TITLE block + input block must share the same `groupUuid`.

## Block Types

### Structure
- `FORM_TITLE` - Form title and submit button
- `TEXT` - Paragraph text
- `HEADING_1`, `HEADING_2`, `HEADING_3` - Section headers
- `TITLE` - Question label (inside QUESTION group)
- `DIVIDER` - Separator line

### Inputs
- `INPUT_TEXT` - Short text
- `INPUT_NUMBER` - Number
- `INPUT_EMAIL` - Email
- `INPUT_DATE` - Date picker
- `INPUT_PHONE_NUMBER` - Phone
- `TEXTAREA` - Long text

### Selection
- `MULTIPLE_CHOICE_OPTION` - Single select (groupType: MULTIPLE_CHOICE)
- `CHECKBOX` - Multi select (groupType: CHECKBOXES)
- `DROPDOWN_OPTION` - Dropdown option

### ⚠️ Types that don't render well via API
- `RATING` - Stars don't display
- `LINEAR_SCALE` - Scale doesn't display

**Workaround:** Use `MULTIPLE_CHOICE_OPTION` with star emojis.

## Examples

### Form title
```json
{
  "uuid": "title-001",
  "type": "FORM_TITLE",
  "groupUuid": "group-title",
  "groupType": "FORM_TITLE",
  "payload": {
    "title": "My Survey",
    "button": {"label": "Submit"}
  }
}
```

### Section header
```json
{
  "uuid": "sec1-head",
  "type": "HEADING_2",
  "groupUuid": "group-sec1",
  "groupType": "TEXT",
  "payload": {
    "safeHTMLSchema": [["📊 Section Title", [["tag", "span"]]]]
  }
}
```

### Text input question
```json
{
  "uuid": "q1-title",
  "type": "TITLE",
  "groupUuid": "group-q1",
  "groupType": "QUESTION",
  "payload": {
    "safeHTMLSchema": [["What is your name?", [["tag", "span"]]]]
  }
},
{
  "uuid": "q1-input",
  "type": "INPUT_TEXT",
  "groupUuid": "group-q1",
  "groupType": "QUESTION",
  "payload": {"isRequired": true}
}
```

### Multiple choice (single answer)
```json
{
  "uuid": "q2-title",
  "type": "TITLE",
  "groupUuid": "group-q2",
  "groupType": "QUESTION",
  "payload": {
    "safeHTMLSchema": [["How did you hear about us?", [["tag", "span"]]]]
  }
},
{
  "uuid": "q2-opt1",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q2",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 0, "isFirst": true, "isLast": false, "text": "Social media"}
},
{
  "uuid": "q2-opt2",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q2",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 1, "isFirst": false, "isLast": true, "text": "Friend referral"}
}
```

### Checkboxes (multiple answers)
```json
{
  "uuid": "q3-title",
  "type": "TITLE",
  "groupUuid": "group-q3",
  "groupType": "QUESTION",
  "payload": {
    "safeHTMLSchema": [["What features interest you?", [["tag", "span"]]]]
  }
},
{
  "uuid": "q3-cb1",
  "type": "CHECKBOX",
  "groupUuid": "group-q3",
  "groupType": "CHECKBOXES",
  "payload": {"index": 0, "isFirst": true, "isLast": false, "text": "Feature A"}
},
{
  "uuid": "q3-cb2",
  "type": "CHECKBOX",
  "groupUuid": "group-q3",
  "groupType": "CHECKBOXES",
  "payload": {"index": 1, "isFirst": false, "isLast": true, "text": "Feature B"}
}
```

### Rating scale (workaround with stars)
```json
{
  "uuid": "q4-title",
  "type": "TITLE",
  "groupUuid": "group-q4",
  "groupType": "QUESTION",
  "payload": {
    "safeHTMLSchema": [["How would you rate our service?", [["tag", "span"]]]]
  }
},
{
  "uuid": "q4-opt1",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q4",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 0, "isFirst": true, "isLast": false, "text": "⭐ Poor"}
},
{
  "uuid": "q4-opt2",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q4",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 1, "isFirst": false, "isLast": false, "text": "⭐⭐ Fair"}
},
{
  "uuid": "q4-opt3",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q4",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 2, "isFirst": false, "isLast": false, "text": "⭐⭐⭐ Good"}
},
{
  "uuid": "q4-opt4",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q4",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 3, "isFirst": false, "isLast": false, "text": "⭐⭐⭐⭐ Very good"}
},
{
  "uuid": "q4-opt5",
  "type": "MULTIPLE_CHOICE_OPTION",
  "groupUuid": "group-q4",
  "groupType": "MULTIPLE_CHOICE",
  "payload": {"isRequired": true, "index": 4, "isFirst": false, "isLast": true, "text": "⭐⭐⭐⭐⭐ Excellent"}
}
```

## Update Command

```bash
TALLY_KEY=$(cat ~/.config/tally/api_key)

# Backup first
curl -s "https://api.tally.so/forms/{ID}" \
  -H "Authorization: Bearer $TALLY_KEY" > /tmp/backup.json

# Update
curl -s "https://api.tally.so/forms/{ID}" \
  -X PATCH \
  -H "Authorization: Bearer $TALLY_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/form.json

# Verify
curl -s "https://api.tally.so/forms/{ID}" \
  -H "Authorization: Bearer $TALLY_KEY" | jq '.blocks | length'
```

## Best Practices

1. **Always backup** before modifying a form
2. **Use descriptive UUIDs** (q1-title, q1-input, sec1-head)
3. **Section titles:** Use lowercase with emoji prefix (📊 General feedback)
4. **For ratings:** Use MULTIPLE_CHOICE with ⭐ emojis instead of RATING type
5. **Verify after update:** Check block count matches expected
