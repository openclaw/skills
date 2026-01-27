---
name: mastodon-publisher
description: Publish content to Mastodon. Use when you need to share updates, posts, or media.
author: Behrang Saeedzadeh
version: 1.0.0
triggers:
  - "post to mastodon"
metadata: { "clawdbot": { "emoji": "🐘" }, "requires": { "bins": ["node"] } }
---

# Mastodon Publisher

Publish content to Mastodon. Use when you need to share updates, posts, or media.

## Usage

### Post a new status to Mastodon

Post a new status to Mastodon with Bun:

```bash
node {baseDir}/scripts/toobot.js new-status \
  --status "some status text" \
  --visibility "public | private | unlisted | direct" \
  --language "ISO-639-1-code" --scheduled-at "RFC3339-date-time" \
  --quote-approval-policy "public | followers | nobody"
```

Parameters

| Name                      | Description                              | Type                                            | Example                    | Required | Default  |
| ------------------------- | ---------------------------------------- | ----------------------------------------------- | -------------------------- | -------- | -------- |
| `--status`                | The text content of the status           | string                                          | "Hello, World"             | yes^1    | N/A      |
| `--visibility`            | Sets the visibility of the posted status | `public` or `private` or `unlisted` or `direct` | "private"                  | no       | "public" |
| `--language`              | ISO 639-1 language code for this status  | ISO-639-1 Language Code                         | "en"                       | no       |          |
| `-scheduled-at`           | Datetime at which to schedule a status   | RFC3339 date time                               | "2029-02-03T15:30:45.000Z" | no       |          |
| `--quote-approval-policy` | Sets who is allowed to quote the status  | `public` or `followrs` or `nobody`              | "nobody"                   | no       |          |
| `--media-path`            | Media to be attached to the status       | path                                            | /path/to/foo.mpg           | no^2     |          |

- ^1 `--status` can be ommitted when one or `--media-path` parameters are present
- ^2 one or `--media-path` parameters must be present if `--status` is ommitted

## Examples

- **Post a new status**

  ```bash
  node {baseDir}/scripts/toobot.js new-status --status "Hello, world!"
  ```

  Read the output and summarize it for the user.

- **Post a scheduled status**

  ```bash
  node {baseDir}/scripts/toobot.js new-status --status "Hello, world!" --scheduled-at 2030-01-02T14:15:16.000Z
  ```

  Read the output and summarize it for the user.

- **Post a scheduled status with visibility, language, quote approval policy, and a single media attachment**

  ```bash
  node {baseDir}/scripts/toobot.js new-status --status "Hello, world!" \
    --scheduled-at 2030-01-02T14:15:16.000Z \
    --visibility private \
    --quote-approval-policy nobody \
    --language en \
    --media-path /path/to/foo.jpg
  ```

  Read the output and summarize it for the user.

- **Post a new status with media multiple attachments**

  ```bash
  node {baseDir}/scripts/toobot.js new-status --status "Hello, world!" --media-path /path/to/foo.jpg --media-path /path/to/bar.jpg
  ```

- **Post a new status with media attachments and no status text**

  ```bash
  bun {baseDir}/scripts/toobot.js new-status --media-path /path/to/media.jpg
  ```

## Notes

- Requires `node` to be installed and available in the PATH.
