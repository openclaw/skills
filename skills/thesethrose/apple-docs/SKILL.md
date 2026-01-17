---
name: apple-docs
description: Query Apple Developer Documentation, APIs, and WWDC videos (2014-2025). Search SwiftUI, UIKit, Objective-C, Swift frameworks and watch sessions.
metadata: {"clawdbot":{"emoji":"🍎","requires":{"bins":["node"]}}}
---

# Apple Docs Skill

Query Apple Developer Documentation, frameworks, APIs, and WWDC videos.

## Setup

No installation required - works out of the box with native fetch.

## Available Tools

### Documentation Search

| Command | Description |
|---------|-------------|
| `apple-docs search "query"` | Search Apple Developer Documentation |
| `apple-docs symbols "UIView"` | Search framework classes, structs, protocols |
| `apple-docs doc "/path/to/doc"` | Get detailed documentation by path |

### API Exploration

| Command | Description |
|---------|-------------|
| `apple-docs apis "UIViewController"` | Find inheritance and protocol conformances |
| `apple-docs platform "UIScrollView"` | Check platform/version compatibility |
| `apple-docs similar "UIPickerView"` | Find Apple's recommended alternatives |

### Technology Browsing

| Command | Description |
|---------|-------------|
| `apple-docs tech` | List all Apple technologies by category |
| `apple-docs overview "SwiftUI"` | Get comprehensive technology guides |
| `apple-docs samples "SwiftUI"` | Browse Swift/Objective-C sample projects |

### WWDC Videos

| Command | Description |
|---------|-------------|
| `apple-docs wwdc-search "async"` | Search WWDC sessions (2014-2025) |
| `apple-docs wwdc-video 2024-100` | Get transcript, code examples, resources |
| `apple-docs wwdc-topics` | List 20 WWDC topic categories |
| `apple-docs wwdc-years` | List WWDC years with video counts |

## Options

| Option | Description |
|--------|-------------|
| `--limit <n>` | Limit number of results |
| `--category` | Filter by technology category |
| `--framework` | Filter by framework name |
| `--year` | Filter by WWDC year |
| `--no-transcript` | Skip transcript for WWDC videos |
| `--no-inheritance` | Skip inheritance info in apis command |
| `--no-conformances` | Skip protocol conformances in apis command |

## Examples

### Search Documentation

```bash
# Search for SwiftUI animations
apple-docs search "SwiftUI animation"

# Find UITableView delegate methods
apple-docs symbols "UITableViewDelegate"
```

### Check Platform Compatibility

```bash
# Check iOS version support for Vision framework
apple-docs platform "VNRecognizeTextRequest"

# Find all SwiftUI views that support iOS 15+
apple-docs search "SwiftUI View iOS 15"
```

### Explore APIs

```bash
# Get inheritance hierarchy for UIViewController
apple-docs apis "UIViewController"

# Find alternatives to deprecated API
apple-docs similar "UILabel"
```

### WWDC Videos

```bash
# Search for async/await sessions
apple-docs wwdc-search "async await"

# Get specific video details with transcript
apple-docs wwdc-video 2024-100

# List all available years
apple-docs wwdc-years
```

### Browse Technologies

```bash
# List all Apple technologies
apple-docs tech

# Get SwiftUI overview guide
apple-docs overview "SwiftUI"

# Find Vision framework samples
apple-docs samples "Vision"
```

## Caching

The underlying MCP server includes:
- 30 minute cache for API docs
- 10 minute cache for search results
- 1 hour cache for framework info
- 1,260+ WWDC videos bundled offline (35MB)

## Resources

- MCP Server: https://github.com/kimsungwhee/apple-docs-mcp
- Apple Developer Documentation: https://developer.apple.com/documentation/
- Apple Developer: https://developer.apple.com/
