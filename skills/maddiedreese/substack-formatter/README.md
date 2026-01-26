# Substack Article Formatter

Transform plain text into professional Substack format. **Ensures proper HTML formatting** so bold/italic/headers work correctly when pasted into Substack editor.

## ✨ Key Features

- **Clean formatting** for better readability
- **Proper HTML output** that Substack editor recognizes
- **Copy-paste ready** with formatting preserved
- **Minimal or standard formatting options**

## 🚀 Quick Start

```bash
# Basic formatting
python3 formatter.py "Your content here"

# With specific structure  
python3 formatter.py "Your content here" micro-story

# Format and copy to clipboard (Linux)
python3 formatter.py "Your content here" | python3 copy_to_substack.py
```

## 📋 Copy-Paste Process

1. **Format your content** using the formatter
2. **Copy as HTML** using the copy script  
3. **Paste into Substack** - formatting preserved automatically!

### Linux/WSL:
```bash
# Install dependencies
sudo apt install pandoc xclip  # Ubuntu/Debian
sudo pacman -S pandoc xclip    # Arch

# Format and copy
python3 formatter.py "Your text" > output.html
python3 copy_to_substack.py "$(cat output.html)"
```

### macOS:
```bash
brew install pandoc
# Use pbcopy instead of xclip (modify copy script as needed)
```

## 🎯 Formatting Options

### **Standard Formatting**
Clean paragraph structure with proper HTML tags

### **Minimal Formatting**  
Pure spacing improvements with exact content preservation

## 🛠 Files

- **`formatter.py`** - Main formatting engine
- **`copy_to_substack.py`** - HTML clipboard utility
- **`test_formatter.py`** - Test all formats
- **`examples.md`** - Before/after examples
- **`SKILL.md`** - Complete documentation

## 🧪 Testing

```bash
# Test all formatting types
python3 test_formatter.py

# Test specific format
python3 formatter.py "Your content" micro-story
```

## 🔧 Integration with Clawdbot

Just tell Clawdbot:

> "Format this for Substack: [your content]"

Or be specific:

> "Format this for Substack as a micro-story: [your content]"

The skill handles:
- Viral pattern application
- HTML conversion  
- Copy instructions
- Formatting verification

## ⚠️ Technical Notes

**Why HTML conversion is needed:** Substack editor treats raw markdown as plain text. The solution is converting to HTML and copying as `text/html` format so Substack recognizes the formatting.

**Dependencies:**
- `pandoc` - Markdown to HTML conversion
- `xclip` (Linux) - Clipboard management with MIME types
- `pbcopy` (macOS) - Alternative clipboard tool

## 🎯 Philosophy

**Format for readability, preserve your voice.** This tool improves visual presentation while keeping your message and personality intact.